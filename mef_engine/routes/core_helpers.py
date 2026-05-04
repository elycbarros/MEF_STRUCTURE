import math
from typing import Any, Optional
from radier_utils import _as_float, sanitize_for_json
from radier_design_v2 import suggest_commercial_reinforcement
from schemas.core import ConfigInput

FIELD_RISK_CATALOG = {
    "heterogeneous_soil": {
        "label": "Solo heterogêneo na cota de apoio",
        "severity": "yellow",
        "action": "Exigir revisão geotécnica, campanha complementar ou kv_map por sondagem.",
    },
    "water_in_excavation": {
        "label": "Água/percolação na cava",
        "severity": "red",
        "action": "Bloquear OK executivo até definir drenagem, rebaixamento ou procedimento de concretagem adequado.",
    },
    "boulders": {
        "label": "Matacões ou blocos de rocha",
        "severity": "red",
        "action": "Não considerar apoio direto local sem remoção, tratamento ou solução alternativa.",
    },
    "altered_rock": {
        "label": "Rocha alterada/decomposta",
        "severity": "yellow",
        "action": "Usar tensão admissível específica da rocha real, sem herdar valor de rocha sã.",
    },
    "expansive_or_collapsible": {
        "label": "Solo expansivo ou colapsível",
        "severity": "red",
        "action": "Radier/fundação rasa não deve ser liberado sem substituição, melhoria do solo ou fundação profunda.",
    },
}

SOIL_PRESET_RISK = {
    "soft_organic": "red",
    "wet_clay": "yellow",
    "medium_clay": "yellow",
    "dry_stiff_clay": "green",
    "sandy_gravel": "green",
    "very_stiff_gravel": "green",
}

DIAGNOSTIC_PROFILES = {
    "permissive": {
        "label": "Permissivo",
        "pressure_alert_ratio": 0.90,
        "pressure_restriction_ratio": 0.98,
        "punching_alert_ratio": 0.90,
        "punching_restriction_ratio": 0.98,
        "settlement_alert_ratio": 0.90,
        "settlement_restriction_ratio": 0.98,
        "distortion_alert_ratio": 0.90,
        "distortion_restriction_ratio": 0.98,
        "cracking_alert_ratio": 0.90,
        "cracking_restriction_ratio": 0.98,
        "winkler_min_ratio": 0.70,
        "winkler_alert_ratio": 0.85,
        "thick_raft_m": 0.90,
        "very_thick_raft_m": 1.20,
        "below_reference_ratio": 0.80,
        "heavy_column_kN": 5500.0,
    },
    "balanced": {
        "label": "Equilibrado",
        "pressure_alert_ratio": 0.85,
        "pressure_restriction_ratio": 0.95,
        "punching_alert_ratio": 0.85,
        "punching_restriction_ratio": 0.95,
        "settlement_alert_ratio": 0.85,
        "settlement_restriction_ratio": 0.95,
        "distortion_alert_ratio": 0.85,
        "distortion_restriction_ratio": 0.95,
        "cracking_alert_ratio": 0.85,
        "cracking_restriction_ratio": 0.95,
        "winkler_min_ratio": 0.80,
        "winkler_alert_ratio": 0.90,
        "thick_raft_m": 0.80,
        "very_thick_raft_m": 1.00,
        "below_reference_ratio": 0.85,
        "heavy_column_kN": 5000.0,
    },
    "conservative": {
        "label": "Conservador",
        "pressure_alert_ratio": 0.75,
        "pressure_restriction_ratio": 0.90,
        "punching_alert_ratio": 0.75,
        "punching_restriction_ratio": 0.90,
        "settlement_alert_ratio": 0.75,
        "settlement_restriction_ratio": 0.90,
        "distortion_alert_ratio": 0.75,
        "distortion_restriction_ratio": 0.90,
        "cracking_alert_ratio": 0.75,
        "cracking_restriction_ratio": 0.90,
        "winkler_min_ratio": 0.90,
        "winkler_alert_ratio": 1.00,
        "thick_raft_m": 0.70,
        "very_thick_raft_m": 0.90,
        "below_reference_ratio": 0.95,
        "heavy_column_kN": 4000.0,
    },
}

def build_field_risk_summary(input: ConfigInput) -> dict[str, Any]:
    severity_rank = {"green": 0, "yellow": 1, "red": 2}
    soil_risk = SOIL_PRESET_RISK.get(input.soil_preset_id or "", "green")
    selected = []
    for risk_id in input.field_risk_ids:
        risk = FIELD_RISK_CATALOG.get(risk_id)
        if not risk:
            continue
        selected.append({"id": risk_id, **risk})

    worst = soil_risk
    for item in selected:
        if severity_rank[item["severity"]] > severity_rank[worst]:
            worst = item["severity"]

    recommendations = [item["action"] for item in selected]
    if soil_risk == "red":
        recommendations.insert(0, "Solo do preset exige mitigacao geotecnica antes de liberar fundacao rasa.")
    elif soil_risk == "yellow":
        recommendations.insert(0, "Confirmar parametros do solo com sondagem, prova de carga ou correlacao validada.")
    if not recommendations:
        recommendations.append("Manter registro das premissas geotecnicas e controle executivo de compactacao, lastro, lona e cura.")

    return {
        "status": worst,
        "selected": selected,
        "recommendations": list(dict.fromkeys(recommendations)),
        "policy": "Itens vermelhos sao condicionantes de engenharia e nao devem ser tratados como simples aviso visual.",
    }

def build_winkler_consistency(input: ConfigInput, deterministic: dict[str, Any]) -> dict[str, Any]:
    area_m2 = input.Lx * input.Ly
    q_service_kPa = deterministic.get("loads_total_kN", 0.0) / max(area_m2, 1e-9)
    kv_kN_m3 = input.kv / 1000.0
    w_expected_mm = (q_service_kPa / max(kv_kN_m3, 1e-9)) * 1000.0
    w_max_mm = deterministic.get("w_max_mm")
    ratio = None
    pass_check = False
    if isinstance(w_max_mm, (int, float)) and w_expected_mm > 0:
        ratio = float(w_max_mm) / w_expected_mm
        pass_check = ratio >= 0.8
    return {
        "q_service_mean_kPa": q_service_kPa,
        "kv_kN_m3": kv_kN_m3,
        "w_expected_mean_mm": w_expected_mm,
        "w_max_mm": w_max_mm,
        "wmax_over_expected_mean": ratio,
        "pass": pass_check,
        "note": "Para base de Winkler uniforme, w_max deve ser compatível com q_media/kv e usualmente nao menor que o recalque medio esperado.",
    }

def build_reinforcement_summary(memorial: dict[str, Any]) -> dict[str, Any]:
    structural = memorial.get("verificacoes_estruturais", {})
    service = memorial.get("verificacoes_de_servico", {})
    flexure = structural.get("flexao", {}) if isinstance(structural, dict) else {}
    punching = structural.get("puncao", {}) if isinstance(structural, dict) else {}
    detailing = memorial.get("detalhamento_final", {})
    ratio_max = _as_float(punching.get("ratio_max"))
    wk_x_ok = service.get("wk_x_ok") if isinstance(service, dict) else None
    wk_y_ok = service.get("wk_y_ok") if isinstance(service, dict) else None
    critical_zones = [
        {
            "zone": "faixas sobre pilares",
            "priority": "alta" if ratio_max >= 0.85 else "media",
            "guidance": "Concentrar armadura superior, conferir ancoragem e prever reforco local quando punção ou momento negativo governarem.",
        },
        {
            "zone": "panos centrais",
            "priority": "media",
            "guidance": "Distribuir armadura inferior principal nas duas direcoes conforme envelopes de momento positivo.",
        },
        {
            "zone": "bordas e cantos",
            "priority": "alta" if ratio_max >= 0.75 else "media",
            "guidance": "Revisar cobrimento, comprimento de ancoragem, torcao local e possiveis reforcos de borda.",
        },
    ]
    if wk_x_ok is False or wk_y_ok is False:
        critical_zones.append(
            {
                "zone": "regioes de fissuracao critica",
                "priority": "alta",
                "guidance": "Aumentar taxa local, reduzir espacamento ou revisar espessura antes de fechar detalhamento.",
            }
        )

    return {
        "status": "available" if flexure else "not_available",
        "flexure": flexure,
        "punching": punching,
        "serviceability": {
            "wk_x_max_mm": service.get("wk_x_max_mm") if isinstance(service, dict) else None,
            "wk_y_max_mm": service.get("wk_y_max_mm") if isinstance(service, dict) else None,
            "wk_limit_mm": service.get("wk_limit_mm") if isinstance(service, dict) else None,
            "wk_x_ok": service.get("wk_x_ok") if isinstance(service, dict) else None,
            "wk_y_ok": service.get("wk_y_ok") if isinstance(service, dict) else None,
        },
        "detailing_guidance": detailing,
        "critical_zones": critical_zones,
        "notes": [
            "Armadura calculada por flexao em faces superior/inferior e direcoes X/Y.",
            "A sugestao comercial e preliminar; detalhamento executivo deve definir faixas, emendas, ancoragens e reforcos locais.",
            "Punção e fissuracao devem governar engrossamentos, capiteis ou reforcos especificos quando necessario.",
        ],
    }

def _resolve_diagnostic_profile(raw_level: str | None) -> tuple[str, dict[str, Any]]:
    level = (raw_level or "balanced").strip().lower()
    if level not in DIAGNOSTIC_PROFILES:
        level = "balanced"
    return level, DIAGNOSTIC_PROFILES[level]

def _service_ratio(checks: list[dict[str, Any]], check_id: str) -> float | None:
    for check in checks:
        if check.get("id") != check_id:
            continue
        actual = _as_float(check.get("actual"), default=float("nan"))
        limit = _as_float(check.get("limit_max"), default=float("nan"))
        if math.isfinite(actual) and math.isfinite(limit) and limit > 0:
            return actual / limit
    return None

def build_foundation_recommendation(input: ConfigInput, memorial: dict[str, Any], deterministic: dict[str, Any], field_risk_summary: dict[str, Any], winkler: dict[str, Any]) -> dict[str, Any]:
    geotech = memorial.get("verificacoes_geotecnicas", {})
    structural = memorial.get("verificacoes_estruturais", {})
    service = memorial.get("verificacoes_de_servico", {})
    predim = memorial.get("pre_dimensionamento", {})
    benchmark = memorial.get("benchmark_evidences", {})
    checklist = memorial.get("checklist_profissional", {})
    punching = structural.get("puncao", {}) if isinstance(structural, dict) else {}
    recalc = service.get("criterios_recalque", {}) if isinstance(service, dict) else {}
    recalc_checks = recalc.get("checks", []) if isinstance(recalc, dict) else []
    recalc_checks = recalc_checks if isinstance(recalc_checks, list) else []

    area_m2 = max(input.Lx * input.Ly, 1e-9)
    aspect_ratio = max(input.Lx, input.Ly) / max(min(input.Lx, input.Ly), 1e-9)
    volume_m3 = area_m2 * input.h
    total_load_kN = _as_float(deterministic.get("loads_total_kN"))
    avg_pressure = total_load_kN / area_m2 if total_load_kN else _as_float(geotech.get("pressao_media_kPa"))
    qmax = _as_float(geotech.get("pressao_max_modelo_kPa"))
    sigma_adm = max(_as_float(geotech.get("tensao_admissivel_kPa"), input.sigma_adm_kPa), 1e-9)
    pressure_ratio = qmax / sigma_adm
    punching_ratio = _as_float(punching.get("ratio_max"))
    total_settlement_ratio = _service_ratio(recalc_checks, "recalque_total")
    differential_settlement_ratio = _service_ratio(recalc_checks, "recalque_diferencial")
    angular_distortion_ratio = _service_ratio(recalc_checks, "distorcao_angular")
    wk_limit = _as_float(service.get("wk_limit_mm"), default=0.0)
    wk_ratio = None
    if wk_limit > 0:
        wk_ratio = max(_as_float(service.get("wk_x_max_mm")), _as_float(service.get("wk_y_max_mm"))) / wk_limit
    thickness_reference = _as_float(predim.get("espessura_referencia_m"))
    thickness_ratio = input.h / max(thickness_reference, 1e-9) if thickness_reference else None
    active_pillars = [] if input.ignore_pillars else (input.pillars or [])
    max_pillar_load = max([pillar.p_kN for pillar in active_pillars], default=0.0)
    diagnostic_level, profile = _resolve_diagnostic_profile(input.diagnostic_conservatism)
    soil_context = input.soil_parameter_context if isinstance(input.soil_parameter_context, dict) else {}
    kv_source = str(soil_context.get("kv_source") or "nao_informado")
    kv_source_label = str(soil_context.get("kv_source_label") or kv_source.replace("_", " "))
    kv_confidence = max(0.0, min(1.0, _as_float(soil_context.get("kv_confidence"), 0.5)))

    triggers: list[dict[str, Any]] = []

    def add_trigger(code: str, technical_level: str, severity: str, message: str, evidence: str) -> None:
        triggers.append(
            {
                "code": code,
                "technical_level": technical_level,
                "severity": severity,
                "message": message,
                "evidence": evidence,
            }
        )

    if geotech.get("atende_pressao_max_modelo") is False:
        add_trigger("soil_pressure_exceeded", "bloqueio", "red", "Pressao maxima no solo excede a tensao admissivel informada.", f"qmax/sigma_adm = {pressure_ratio:.2f}")
    elif pressure_ratio >= profile["pressure_restriction_ratio"]:
        add_trigger("soil_pressure_restriction", "restricao", "yellow", "Pressao maxima no solo esta em faixa muito proxima do limite admissivel.", f"qmax/sigma_adm = {pressure_ratio:.2f}")
    elif pressure_ratio >= profile["pressure_alert_ratio"]:
        add_trigger("soil_pressure_high", "alerta", "yellow", "Pressao maxima esta proxima do limite admissivel.", f"qmax/sigma_adm = {pressure_ratio:.2f}")

    if punching.get("atende") is False:
        add_trigger("punching_failure", "bloqueio", "red", "Punção nao atende para radier liso sem reforco local.", f"eta_puncao = {punching_ratio:.2f}")
    elif punching_ratio >= profile["punching_restriction_ratio"]:
        add_trigger("punching_restriction", "restricao", "yellow", "Punção esta em margem estreita; prever reforco local ou revisar tipologia.", f"eta_puncao = {punching_ratio:.2f}")
    elif punching_ratio >= profile["punching_alert_ratio"]:
        add_trigger("punching_high", "alerta", "yellow", "Punção esta proxima do limite; estudar engrossamento, pedestal/cogumelo ou nervuras.", f"eta_puncao = {punching_ratio:.2f}")

    if recalc.get("atende_global") is False:
        add_trigger("settlement_failure", "bloqueio", "red", "Recalque/distorcao angular nao atende aos limites orientativos.", f"wmax = {_as_float(service.get('w_max_mm')):.2f} mm")
    else:
        service_ratios = [
            ("settlement_total_high", "Recalque total esta proximo do limite orientativo.", total_settlement_ratio),
            ("settlement_differential_high", "Recalque diferencial esta proximo do limite orientativo.", differential_settlement_ratio),
            ("angular_distortion_high", "Distorcao angular esta proxima do limite orientativo.", angular_distortion_ratio),
        ]
        for code, message, ratio in service_ratios:
            if ratio is None:
                continue
            alert_threshold = profile["distortion_alert_ratio"] if code == "angular_distortion_high" else profile["settlement_alert_ratio"]
            restriction_threshold = profile["distortion_restriction_ratio"] if code == "angular_distortion_high" else profile["settlement_restriction_ratio"]
            if ratio >= restriction_threshold:
                add_trigger(code.replace("_high", "_restriction"), "restricao", "yellow", message.replace("proximo do", "em margem estreita frente ao"), f"uso/limite = {ratio:.2f}")
            elif ratio >= alert_threshold:
                add_trigger(code, "alerta", "yellow", message, f"uso/limite = {ratio:.2f}")

    if service.get("wk_x_ok") is False or service.get("wk_y_ok") is False:
        add_trigger("cracking_failure", "restricao", "yellow", "Fissuracao em servico exige revisao de armadura, espessura ou faixas de reforco.", f"wk_x_ok={service.get('wk_x_ok')} | wk_y_ok={service.get('wk_y_ok')}")
    elif wk_ratio is not None and wk_ratio >= profile["cracking_restriction_ratio"]:
        add_trigger("cracking_restriction", "restricao", "yellow", "Fissuracao em servico esta em margem estreita frente ao limite adotado.", f"wk/limite = {wk_ratio:.2f}")
    elif wk_ratio is not None and wk_ratio >= profile["cracking_alert_ratio"]:
        add_trigger("cracking_high", "alerta", "yellow", "Fissuracao em servico esta proxima do limite adotado.", f"wk/limite = {wk_ratio:.2f}")

    if benchmark.get("blocks_professional_use", not benchmark.get("all_passed", False)):
        add_trigger("benchmark_failure", "bloqueio", "red", "Benchmark interno falhou; nao usar resultados para detalhamento sem revalidacao.", f"suite={benchmark.get('suite_name', 'n/d')}")

    winkler_ratio = _as_float(winkler.get("wmax_over_expected_mean"), default=float("nan"))
    if math.isfinite(winkler_ratio) and winkler_ratio < profile["winkler_min_ratio"]:
        add_trigger("winkler_inconsistency", "bloqueio", "red", "Resposta de recalque esta inconsistente com a estimativa media de Winkler.", f"wmax/wmedio = {winkler_ratio:.2f}")
    elif not math.isfinite(winkler_ratio) and winkler.get("pass") is False:
        add_trigger("winkler_inconsistency", "bloqueio", "red", "Resposta de recalque esta inconsistente com a estimativa media de Winkler.", f"wmax/wmedio = {winkler.get('wmax_over_expected_mean')}")
    elif math.isfinite(winkler_ratio) and winkler_ratio < profile["winkler_alert_ratio"]:
        add_trigger("winkler_low_margin", "alerta", "yellow", "Recalque maximo ficou pouco acima da estimativa media de Winkler; revisar rigidez, cargas e bordas.", f"wmax/wmedio = {winkler_ratio:.2f}")

    if input.h >= profile["very_thick_raft_m"]:
        add_trigger("very_thick_raft", "restricao", "yellow", "Espessura adotada alta para radier liso; avaliar construtibilidade e alternativas.", f"h = {input.h:.2f} m")
    elif input.h >= profile["thick_raft_m"]:
        add_trigger("thick_raft", "alerta", "yellow", "Espessura elevada pode indicar solucao pouco economica para radier liso.", f"h = {input.h:.2f} m")

    if thickness_ratio is not None and thickness_ratio < profile["below_reference_ratio"]:
        add_trigger("below_pre_dimension", "restricao", "yellow", "Espessura adotada esta abaixo da referencia preliminar.", f"h/h_ref = {thickness_ratio:.2f}")

    if field_risk_summary.get("status") == "red":
        add_trigger("field_risk_red", "bloqueio", "red", "Risco de campo vermelho impede liberacao simples de fundacao rasa.", "ver triagem geotecnica/executiva")
    elif field_risk_summary.get("status") == "yellow":
        add_trigger("field_risk_yellow", "restricao", "yellow", "Risco de campo exige confirmacao geotecnica antes do projeto executivo.", "ver triagem geotecnica/executiva")

    if input.soil_preset_id in {"soft_organic", "wet_clay"}:
        add_trigger("soft_soil_preset", "alerta", "yellow", "Preset de solo sugere atenção a recalques e variabilidade do subleito.", f"solo={input.soil_preset_id}")

    if kv_confidence < 0.45:
        add_trigger(
            "kv_low_confidence",
            "restricao",
            "yellow",
            "Coeficiente de reação vertical informado com baixa confiabilidade; calibrar por ensaio, correlação ou análise de recalque.",
            f"origem={kv_source_label} | confianca={kv_confidence:.2f}",
        )
    elif kv_confidence < 0.70:
        add_trigger(
            "kv_medium_confidence",
            "alerta",
            "yellow",
            "Coeficiente de reação vertical exige sensibilidade antes de fechar o dimensionamento.",
            f"origem={kv_source_label} | confianca={kv_confidence:.2f}",
        )

    if max_pillar_load >= profile["heavy_column_kN"]:
        add_trigger("heavy_columns", "alerta", "yellow", "Cargas concentradas altas podem governar punção e reforços locais.", f"Pmax = {max_pillar_load:.0f} kN")

    if input.ignore_pillars or len(active_pillars) == 0:
        add_trigger(
            "uniform_load_only",
            "alerta",
            "yellow",
            "Caso sem pilares/cargas concentradas: recalque uniforme e punção não aplicável; para pátios, verificar roda, fadiga e juntas.",
            "modelo com carga distribuida pura",
        )

    contact_loss_fraction = _as_float(deterministic.get("contact_loss_fraction"), default=0.0)
    w_max_mm = _as_float(service.get("w_max_mm"), default=0.0)
    w_min_mm = _as_float(deterministic.get("w_min_mm"), default=0.0)
    if contact_loss_fraction == 0.0 and w_min_mm < -0.001:
        contact_loss_fraction = 0.03
    if contact_loss_fraction > 0.05:
        add_trigger(
            "tension_contact_loss",
            "bloqueio",
            "red",
            "Perda de contato solo-radier detectada em mais de 5% da área (tracao nas molas). Revisar geometria, rigidez e carregamentos.",
            f"fracao_sem_contato = {contact_loss_fraction:.2f}",
        )
    elif contact_loss_fraction > 0.01:
        add_trigger(
            "tension_contact_loss",
            "restricao",
            "yellow",
            "Indícios de perda de contato solo-radier em região localizada (tracao residual). Verificar bordas, variação de kv e cargas excêntricas.",
            f"fracao_sem_contato = {contact_loss_fraction:.2f}",
        )
    elif contact_loss_fraction > 0.0:
        add_trigger(
            "tension_contact_loss",
            "alerta",
            "yellow",
            "Sinal residual de tração pontual nas molas de Winkler. Monitorar em cenários de carga excêntrica.",
            f"fracao_sem_contato = {contact_loss_fraction:.2f}",
        )

    if w_max_mm > 20.0:
        add_trigger(
            "high_settlement_warning",
            "restricao",
            "yellow",
            "Recalque máximo acima de 20 mm: faixa de maior rigor normativo. Exige análise detalhada de compatibilidade com a superestrutura.",
            f"w_max = {w_max_mm:.1f} mm",
        )
    elif w_max_mm > 10.0:
        add_trigger(
            "high_settlement_warning",
            "alerta",
            "yellow",
            "Recalque máximo entre 10 e 20 mm: faixa de atenção. Avaliar sensibilidade ao kv e compatibilidade estrutural.",
            f"w_max = {w_max_mm:.1f} mm",
        )

    red_count = sum(1 for item in triggers if item["severity"] == "red")
    yellow_count = sum(1 for item in triggers if item["severity"] == "yellow")
    blocking_count = sum(1 for item in triggers if item["technical_level"] == "bloqueio")
    restriction_count = sum(1 for item in triggers if item["technical_level"] == "restricao")
    alert_count = sum(1 for item in triggers if item["technical_level"] == "alerta")

    if blocking_count >= 2 or checklist.get("status") == "nao_apto_requer_revisao_tecnica":
        classification = "estudar_solucao_alternativa"
        main_recommendation = "Nao seguir para detalhamento do radier liso; estudar radier estaqueado, fundacao profunda, radier nervurado/engrossado ou mudanca de sistema."
        decision_rank = 4
        executive_label = "Estudar solução alternativa"
    elif blocking_count == 1:
        classification = "radier_liso_nao_recomendado_sem_revisao"
        main_recommendation = "Radier liso depende de revisao tecnica do gatilho critico antes de qualquer detalhamento executivo."
        decision_rank = 3
        executive_label = "Radier liso não liberado"
    elif restriction_count >= 2 or (restriction_count >= 1 and alert_count >= 2):
        classification = "radier_liso_viavel_com_restricoes"
        main_recommendation = "Radier liso pode permanecer em estudo, mas comparar com sapatas, radier com reforcos locais e melhoria de solo."
        decision_rank = 2
        executive_label = "Viável com restrições"
    elif restriction_count > 0 or alert_count > 0:
        classification = "radier_liso_viavel_com_alertas"
        main_recommendation = "Radier liso preliminarmente viavel, condicionado a validacao geotecnica e detalhamento das regioes criticas."
        decision_rank = 1
        executive_label = "Viável com alertas"
    else:
        classification = "radier_liso_viavel_preliminarmente"
        main_recommendation = "Radier liso coerente para estudo preliminar; prosseguir com detalhamento e validacoes executivas."
        decision_rank = 0
        executive_label = "Viável preliminarmente"

    priority_actions = []
    for item in triggers:
        level = item["technical_level"]
        if level == "bloqueio":
            priority_actions.append(f"Tratar bloqueio: {item['message']} ({item['evidence']}).")
        elif level == "restricao":
            priority_actions.append(f"Resolver restricao: {item['message']} ({item['evidence']}).")
        elif item["code"] == "uniform_load_only":
            priority_actions.append("Complementar como piso/patio: carga de roda, fadiga, juntas serradas/retracao e preparo do subleito.")
    if not priority_actions:
        priority_actions.extend(
            [
                "Consolidar faixas de armadura e reforcos locais.",
                "Registrar premissas geotecnicas e revisar com o responsavel tecnico.",
                "Comparar pelo menos um cenario de sensibilidade de kv e sigma_adm.",
            ]
        )

    diagnostic_thresholds = {
        "pressure_alert_ratio": profile["pressure_alert_ratio"],
        "pressure_restriction_ratio": profile["pressure_restriction_ratio"],
        "punching_alert_ratio": profile["punching_alert_ratio"],
        "punching_restriction_ratio": profile["punching_restriction_ratio"],
        "settlement_alert_ratio": profile["settlement_alert_ratio"],
        "settlement_restriction_ratio": profile["settlement_restriction_ratio"],
        "distortion_alert_ratio": profile["distortion_alert_ratio"],
        "distortion_restriction_ratio": profile["distortion_restriction_ratio"],
        "cracking_alert_ratio": profile["cracking_alert_ratio"],
        "cracking_restriction_ratio": profile["cracking_restriction_ratio"],
        "winkler_min_ratio": profile["winkler_min_ratio"],
        "winkler_alert_ratio": profile["winkler_alert_ratio"],
        "thick_raft_m": profile["thick_raft_m"],
        "very_thick_raft_m": profile["very_thick_raft_m"],
    }

    alternatives = [
        {
            "solution": "Sapatas isoladas/corridas/associadas",
            "when_to_study": "Solo superficial competente, cargas moderadas e pilares suficientemente afastados.",
        },
        {
            "solution": "Radier com pedestais/cogumelos ou engrossamentos",
            "when_to_study": "Punção ou momentos locais governam, mas o solo e os recalques permanecem aceitaveis.",
        },
        {
            "solution": "Radier nervurado",
            "when_to_study": "Necessidade de maior rigidez flexional sem transformar toda a laje em espessura maciça elevada.",
        },
        {
            "solution": "Radier estaqueado / piled raft",
            "when_to_study": "Recalques, solo mole/heterogeneo ou cargas concentradas indicam transferencia parcial para camadas profundas.",
        },
        {
            "solution": "Fundação profunda independente",
            "when_to_study": "Solo superficial inadequado, risco executivo elevado ou inviabilidade economica/geometrica da fundacao rasa.",
        },
    ]

    return {
        "classification": classification,
        "executive_label": executive_label,
        "decision_rank": decision_rank,
        "main_recommendation": main_recommendation,
        "priority_actions": list(dict.fromkeys(priority_actions))[:6],
        "trigger_counts": {"red": red_count, "yellow": yellow_count, "total": len(triggers)},
        "technical_level_counts": {
            "alerta": alert_count,
            "restricao": restriction_count,
            "bloqueio": blocking_count,
            "total": len(triggers),
        },
        "diagnostic_conservatism": {
            "id": diagnostic_level,
            "label": profile["label"],
            "thresholds": diagnostic_thresholds,
        },
        "input_policy": {
            "ignore_pillars": bool(input.ignore_pillars),
            "active_pillar_count": len(active_pillars),
            "kv_source": kv_source,
            "kv_source_label": kv_source_label,
            "kv_confidence": kv_confidence,
        },
        "metrics": {
            "area_m2": area_m2,
            "aspect_ratio": aspect_ratio,
            "volume_m3": volume_m3,
            "avg_pressure_kPa": avg_pressure,
            "pressure_ratio": pressure_ratio,
            "punching_ratio": punching_ratio,
            "total_settlement_ratio": total_settlement_ratio,
            "differential_settlement_ratio": differential_settlement_ratio,
            "angular_distortion_ratio": angular_distortion_ratio,
            "cracking_ratio": wk_ratio,
            "winkler_ratio": winkler_ratio if math.isfinite(winkler_ratio) else None,
            "thickness_reference_m": thickness_reference,
            "thickness_ratio": thickness_ratio,
            "max_pillar_load_kN": max_pillar_load,
            "kv_kN_m3": input.kv / 1000.0,
            "kv_confidence": kv_confidence,
        },
        "triggers": triggers,
        "alternatives": alternatives,
        "scope_note": "Diagnostico orientativo. O sistema atual calcula radier liso em Winkler; radier estaqueado exige modelo de interacao solo-estrutura-estaca.",
        "contact_loss_fraction": contact_loss_fraction,
        "w_max_mm": w_max_mm,
    }

def build_executive_decision_summary(foundation_recommendation: dict[str, Any]) -> dict[str, Any]:
    classification = str(foundation_recommendation.get("classification") or "sem_diagnostico")
    rank = int(_as_float(foundation_recommendation.get("decision_rank"), 99))
    technical_counts = foundation_recommendation.get("technical_level_counts", {})
    metrics = foundation_recommendation.get("metrics", {})
    input_policy = foundation_recommendation.get("input_policy", {})
    priority_actions = foundation_recommendation.get("priority_actions", [])

    if rank >= 4:
        decision_status = "estudar_alternativa"
        go_no_go = "no_go"
        next_step = "Interromper detalhamento do radier liso e comparar solucoes alternativas."
    elif rank == 3:
        decision_status = "nao_liberado"
        go_no_go = "hold"
        next_step = "Resolver bloqueio tecnico antes de avancar para detalhamento executivo."
    elif rank == 2:
        decision_status = "viavel_com_restricoes"
        go_no_go = "conditional_go"
        next_step = "Comparar alternativas e tratar restricoes antes de liberar projeto executivo."
    elif rank == 1:
        decision_status = "viavel_com_alertas"
        go_no_go = "conditional_go"
        next_step = "Prosseguir em estudo preliminar com sensibilidade geotecnica e detalhamento das zonas criticas."
    else:
        decision_status = "viavel_preliminarmente"
        go_no_go = "go_preliminar"
        next_step = "Prosseguir para detalhamento preliminar, mantendo validacao geotecnica e revisao tecnica."

    return {
        "decision_status": decision_status,
        "go_no_go": go_no_go,
        "executive_label": foundation_recommendation.get("executive_label", classification),
        "classification": classification,
        "decision_rank": rank,
        "main_recommendation": foundation_recommendation.get("main_recommendation"),
        "next_step": next_step,
        "first_priority_action": priority_actions[0] if isinstance(priority_actions, list) and priority_actions else next_step,
        "alert_count": technical_counts.get("alerta", 0) if isinstance(technical_counts, dict) else 0,
        "restriction_count": technical_counts.get("restricao", 0) if isinstance(technical_counts, dict) else 0,
        "blocking_count": technical_counts.get("bloqueio", 0) if isinstance(technical_counts, dict) else 0,
        "pressure_ratio": metrics.get("pressure_ratio") if isinstance(metrics, dict) else None,
        "punching_ratio": metrics.get("punching_ratio") if isinstance(metrics, dict) else None,
        "settlement_ratio": metrics.get("total_settlement_ratio") if isinstance(metrics, dict) else None,
        "kv_confidence": input_policy.get("kv_confidence") if isinstance(input_policy, dict) else None,
        "scope_note": foundation_recommendation.get("scope_note"),
    }

def build_regional_reinforcement_map(memorial: dict[str, Any], input: ConfigInput) -> dict[str, Any]:
    flexure = memorial.get("verificacoes_estruturais", {}).get("flexao", {}) if isinstance(memorial.get("verificacoes_estruturais"), dict) else {}
    asx_top = _as_float(flexure.get("Asx_top_adot_max_cm2_m"))
    asy_top = _as_float(flexure.get("Asy_top_adot_max_cm2_m"))
    asx_bot = _as_float(flexure.get("Asx_bottom_adot_max_cm2_m"))
    asy_bot = _as_float(flexure.get("Asy_bottom_adot_max_cm2_m"))
    as_min = _as_float(flexure.get("As_min_face_cm2_m"))

    fator_pilar_top = 1.0
    fator_pilar_bot = 0.60
    fator_pano_top = 0.50
    fator_pano_bot = 1.0
    fator_borda_top = 0.70
    fator_borda_bot = 0.70

    def _region(asx_f: float, asy_f: float, as_min_v: float) -> dict:
        asx = max(asx_f, as_min_v)
        asy = max(asy_f, as_min_v)
        return {
            "Asx_cm2_m": round(asx, 3),
            "Asy_cm2_m": round(asy, 3),
            "sugestao_x": suggest_commercial_reinforcement(asx),
            "sugestao_y": suggest_commercial_reinforcement(asy),
        }

    zones = {
        "faixa_pilar_superior": _region(asx_top * fator_pilar_top, asy_top * fator_pilar_top, as_min),
        "faixa_pilar_inferior": _region(asx_bot * fator_pilar_bot, asy_bot * fator_pilar_bot, as_min),
        "pano_central_superior": _region(asx_top * fator_pano_top, asy_top * fator_pano_top, as_min),
        "pano_central_inferior": _region(asx_bot * fator_pano_bot, asy_bot * fator_pano_bot, as_min),
        "borda_superior": _region(asx_top * fator_borda_top, asy_top * fator_borda_top, as_min),
        "borda_inferior": _region(asx_bot * fator_borda_bot, asy_bot * fator_borda_bot, as_min),
    }

    # Alerta de reforço local: quando pico pilar > 1.5× pano central
    pico_x = zones["faixa_pilar_superior"]["Asx_cm2_m"]
    medio_x = zones["pano_central_superior"]["Asx_cm2_m"]
    requer_reforco_local = pico_x > 1.5 * max(medio_x, 1e-9) if medio_x > 0 else False

    return {
        "zones": zones,
        "as_min_face_cm2_m": as_min,
        "requer_reforco_local": requer_reforco_local,
        "nota": (
            "Faixas calculadas com fatores regionais típicos de radier Winkler. "
            "Detalhamento executivo deve ser feito por engenheiro responsável com análise das envoltórias reais."
        ),
    }

def build_thermal_checklist(input: ConfigInput) -> dict[str, Any]:
    threshold = 0.80
    applicable = input.h >= threshold
    items = []
    if applicable:
        items = [
            {"id": "thermal_study", "description": "Estudo térmico prévio à concretagem (simulação de hidratação)", "priority": "alta"},
            {"id": "pour_plan", "description": "Plano de concretagem: etapas, juntas de construção e sequência de lançamento", "priority": "alta"},
            {"id": "launch_temperature", "description": "Controle de temperatura de lançamento (≤ 30°C recomendado)", "priority": "alta"},
            {"id": "maturity_monitoring", "description": "Monitoramento de maturidade e temperatura interna durante a cura", "priority": "media"},
            {"id": "ettringite_risk", "description": "Avaliação do risco de fissuração térmica e etringita tardia", "priority": "media"},
            {"id": "cooling_measures", "description": "Medidas de resfriamento: agregados pré-resfriados, gelo, ou resfriamento pós-lançamento", "priority": "media"},
            {"id": "curing_plan", "description": "Plano de cura úmida por no mínimo 7 dias com controle de gradiente térmico", "priority": "alta"},
        ]
    return {
        "applicable": applicable,
        "threshold_m": threshold,
        "h_adopted_m": input.h,
        "items": items,
        "nota": (
            "Radiers com espessura ≥ 0.80 m são classificados como concreto massa segundo critérios técnicos brasileiros. "
            "O calor de hidratação pode causar gradientes térmicos internos superiores a 20°C, gerando fissuras de origem térmica."
        ) if applicable else "Espessura abaixo do limiar de concreto massa (0.80 m). Checklist não aplicável.",
    }

def build_solution_comparison(input: ConfigInput, foundation_recommendation: dict[str, Any]) -> dict[str, Any]:
    rank = int(_as_float(foundation_recommendation.get("decision_rank"), 99))
    triggers = foundation_recommendation.get("triggers", [])
    blocking = sum(1 for t in triggers if t.get("technical_level") == "bloqueio")
    pressure_ratio = _as_float(foundation_recommendation.get("metrics", {}).get("pressure_ratio"))
    punching_ratio = _as_float(foundation_recommendation.get("metrics", {}).get("punching_ratio"))

    radier_liso_viability = foundation_recommendation.get("executive_label", "N/D")
    sapatas_hint = "Estudar" if blocking >= 1 or pressure_ratio > 0.90 else "Alternativa madura"
    radier_reforcos_hint = "Estudar" if punching_ratio > 0.80 else "Reserva técnica"
    nervurado_hint = "Estudar" if input.h > 0.90 else "Reserva técnica"

    solutions = [
        {
            "id": "radier_liso",
            "nome": "Radier liso (Winkler)",
            "maturidade": "implementado",
            "viabilidade": radier_liso_viability,
            "quando_estudar": "Solução atual calculada. Viável quando solo uniforme, cargas distribuídas e recalques dentro dos limites.",
            "disponivel": True,
        },
        {
            "id": "sapatas",
            "nome": "Sapatas isoladas / corridas",
            "maturidade": "orientativo",
            "viabilidade": sapatas_hint,
            "quando_estudar": "Solo superficial competente, pilares suficientemente afastados e cargas moderadas.",
            "disponivel": False,
        },
        {
            "id": "radier_reforcos",
            "nome": "Radier com pedestais / cogumelos",
            "maturidade": "orientativo",
            "viabilidade": radier_reforcos_hint,
            "quando_estudar": "Punção ou momentos locais governam mas solo e recalques permanecem aceitáveis.",
            "disponivel": False,
        },
        {
            "id": "radier_nervurado",
            "nome": "Radier nervurado",
            "maturidade": "planejado",
            "viabilidade": nervurado_hint,
            "quando_estudar": "Necessidade de rigidez flexional maior sem transformar toda a laje em espessura maciça elevada.",
            "disponivel": False,
        },
        {
            "id": "radier_estaqueado",
            "nome": "Radier estaqueado (piled raft)",
            "maturidade": "fora_do_escopo",
            "viabilidade": "Fora do escopo atual",
            "quando_estudar": "Solo mole/heterogêneo, recalques inaceitáveis ou cargas muito concentradas exigindo transferência para camadas profundas.",
            "disponivel": False,
        },
        {
            "id": "fundacao_profunda",
            "nome": "Fundação profunda independente",
            "maturidade": "fora_do_escopo",
            "viabilidade": "Fora do escopo atual",
            "quando_estudar": "Solo superficial inadequado, risco executivo elevado ou inviabilidade econômica/geométrica de fundação rasa.",
            "disponivel": False,
        },
    ]

    return {
        "solutions": solutions,
        "nota": (
            "Comparativo qualitativo orientativo. Somente o radier liso está implementado e calculado neste módulo. "
            "As demais soluções requerem modelos físicos distintos e análise de engenheiro responsável."
        ),
        "radier_liso_decision_rank": rank,
    }

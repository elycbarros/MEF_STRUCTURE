from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class SectionProperties:
    area: float
    Ix: float
    Iy: float
    Ixy: float
    cx: float
    cy: float
    Wxmin: float
    Wxmax: float
    Wymin: float
    Wymax: float


class SectionDesigner:
    """
    Calcula propriedades geométricas de seções transversais poligonais genéricas.
    Utilizado para pilares especiais e vigas de seção variável.
    """

    @staticmethod
    def calculate_properties(vertices: List[Tuple[float, float]]) -> SectionProperties:
        """
        Calcula propriedades usando o teorema de Green (fórmulas de área e inércia para polígonos).
        vertices: Lista de (x, y) em metros, em ordem anti-horária.
        """
        n = len(vertices)
        if n < 3:
            raise ValueError('Um polígono deve ter pelo menos 3 vértices.')

        # Garante que o polígono está fechado
        if vertices[0] != vertices[-1]:
            vertices.append(vertices[0])
            n += 1

        area = 0.0
        cx = 0.0
        cy = 0.0
        Ix = 0.0
        Iy = 0.0
        Ixy = 0.0

        for i in range(n - 1):
            xi, yi = vertices[i]
            xj, yj = vertices[i + 1]

            common = xi * yj - xj * yi
            area += common
            cx += (xi + xj) * common
            cy += (yi + yj) * common
            Ix += (yi**2 + yi * yj + yj**2) * common
            Iy += (xi**2 + xi * xj + xj**2) * common
            Ixy += (xi * yj + 2 * xi * yi + 2 * xj * yj + xj * yi) * common

        area /= 2.0
        cx /= 6.0 * area
        cy /= 6.0 * area
        Ix /= 12.0
        Iy /= 12.0
        Ixy /= 24.0

        # Transfere para o centro de gravidade (Teorema dos Eixos Paralelos)
        Ix_cg = Ix - area * cy**2
        Iy_cg = Iy - area * cx**2
        Ixy_cg = Ixy - area * cx * cy

        # Módulos de resistência (W = I / y_max)
        x_coords = [v[0] for v in vertices]
        y_coords = [v[1] for v in vertices]

        dy_max = max(y_coords) - cy
        dy_min = cy - min(y_coords)
        dx_max = max(x_coords) - cx
        dx_min = cx - min(x_coords)

        Wxmax = Ix_cg / dy_max if dy_max > 0 else 0
        Wxmin = Ix_cg / dy_min if dy_min > 0 else 0
        Wymax = Iy_cg / dx_max if dx_max > 0 else 0
        Wymin = Iy_cg / dx_min if dx_min > 0 else 0

        return SectionProperties(
            area=abs(area),
            Ix=abs(Ix_cg),
            Iy=abs(Iy_cg),
            Ixy=Ixy_cg,
            cx=cx,
            cy=cy,
            Wxmin=Wxmin,
            Wxmax=Wxmax,
            Wymin=Wymin,
            Wymax=Wymax,
        )


if __name__ == '__main__':
    # Teste com retângulo 20x50cm
    v = [(0, 0), (0.2, 0), (0.2, 0.5), (0, 0.5)]
    props = SectionDesigner.calculate_properties(v)
    print(f'Área: {props.area:.4f} m² (Esperado: 0.1000)')
    print(f'Ix: {props.Ix:.6f} m⁴ (Esperado: 0.002083)')
    print(f'CG: ({props.cx:.3f}, {props.cy:.3f})')

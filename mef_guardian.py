import subprocess
import time
import sys
import os
import signal

# Configurações
BACKEND_DIR = "mef_engine"
FRONTEND_DIR = "mef_frontend"
BACKEND_CMD = ["python3", "api.py"]
FRONTEND_CMD = ["npm", "run", "dev"]

processes = {}

def start_process(name, cmd, cwd):
    print(f"[*] Iniciando {name}...")
    log_file = open(f"{name.lower()}.log", "w")
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=log_file, stderr=log_file)
    processes[name] = {"proc": proc, "cmd": cmd, "cwd": cwd, "log": log_file}
    return proc

def kill_existing():
    print("[!] Limpando processos antigos nas portas 8000 e 3000...")
    subprocess.run("lsof -ti:8000 | xargs kill -9", shell=True, stderr=subprocess.DEVNULL)
    subprocess.run("lsof -ti:3000 | xargs kill -9", shell=True, stderr=subprocess.DEVNULL)

def main():
    kill_existing()
    
    start_process("Backend", BACKEND_CMD, BACKEND_DIR)
    start_process("Frontend", FRONTEND_CMD, FRONTEND_DIR)
    
    print("\n[+] MEF STRUCTURAL GUARDIAN ATIVO")
    print("[+] Backend: http://localhost:8000")
    print("[+] Frontend: http://localhost:3000")
    print("[+] Pressione Ctrl+C para encerrar tudo.\n")

    try:
        while True:
            for name, data in processes.items():
                if data["proc"].poll() is not None:
                    print(f"[!] {name} caiu! Reiniciando em 3 segundos...")
                    time.sleep(3)
                    start_process(name, data["cmd"], data["cwd"])
            time.sleep(5)
    except KeyboardInterrupt:
        print("\n[!] Encerrando todos os processos...")
        for name, data in processes.items():
            data["proc"].terminate()
            data["log"].close()
        sys.exit(0)

if __name__ == "__main__":
    main()

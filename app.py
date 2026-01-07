import socket
import time
import tkinter as tk  

ips = ['192.168.50.240']  # Adicione novos IPs aqui
portas = [9091]  # Adicione novas portas aqui

sock = None

for ip, porta in zip(ips, portas):
    while True:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, porta))
            # deixa um timeout curto para evitar travar a UI em recv
            sock.settimeout(1.0)
            break
        except socket.error as e:
            if sock:
                try:
                    sock.close()
                except Exception:
                    pass
                sock = None
            print(f"Falha ao conectar à balança em {ip}:{porta}: {e}. Tentando novamente em 5s...")
            time.sleep(5)

def _recv_text():
    """Recebe bytes do socket e decodifica com fallback de encoding.
    Retorna string (possivelmente vazia) quando não há dados no intervalo do timeout.
    """
    try:
        data = sock.recv(1024)
        if not data:
            return ""
        try:
            return data.decode('utf-8', errors='strict').strip()
        except UnicodeDecodeError:
            # fallback comum para dispositivos que enviam ISO-8859-1/Windows-1252
            try:
                return data.decode('latin-1', errors='ignore').strip()
            except Exception:
                # última tentativa: representar em hex para debug
                return data.hex()
    except socket.timeout:
        return ""
    except Exception as e:
        print(f"Erro ao receber dados: {e}")
        return ""

def capturar_peso():
    while True:
        peso = _recv_text()
        if peso:
            print(f'Peso capturado: {peso}')
        
            with open('pesos.txt', 'a') as arquivo:
                arquivo.write(f'{peso}\n')
        time.sleep(0.2)  

def atualizar_peso():
    peso = _recv_text()
    if peso:
        peso_label.config(text=f'Peso capturado: {peso}')  
    # reagenda rapidamente para não travar UI; leitura é não-bloqueante via timeout
    root.after(200, atualizar_peso)  

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("Monitor de Peso")
        root.geometry("1024x300")
        root.configure(bg="#ffffff")
        
        peso_label = tk.Label(
            root,
            text="Peso capturado: ",
            font=("Arial", 16, "bold"),
            bg="#ffffff",
            fg="#111111",
            anchor="center"
        )
        peso_label.pack(expand=True, fill="both", padx=40, pady=40)
        
        atualizar_peso()  
        root.mainloop()  
    except KeyboardInterrupt:
        print("Captura interrompida.")
    finally:
        try:
            if sock:
                sock.close()
        except Exception:
            pass
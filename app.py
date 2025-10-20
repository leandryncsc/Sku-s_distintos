import socket
import time
import tkinter as tk  

ips = ['192.168.50.251']  # Adicione novos IPs aqui
portas = [9091, 9002,9001]  # Adicione novas portas aqui

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

for ip, porta in zip(ips, portas):
    while True:
        try:
            sock.connect((ip, porta))
            break
        except socket.error:
            print(f"Tentando conectar à balança em {ip}:{porta}...")
            time.sleep(5)

def capturar_peso():
    while True:
        peso = sock.recv(1024).decode('utf-8').strip()  
        print(f'Peso capturado: {peso}')
        
        with open('pesos.txt', 'a') as arquivo:
            arquivo.write(f'{peso}\n')
        time.sleep(1)  

def atualizar_peso():
    peso = sock.recv(1024).decode('utf-8').strip()  
    peso_label.config(text=f'Peso capturado: {peso}')  
    root.after(1000, atualizar_peso)  

if __name__ == "__main__":
    try:
        root = tk.Tk()
        root.title("Monitor de Peso")
        root.geometry("300x150")
        
        peso_label = tk.Label(root, text="Peso capturado: ", font=("Arial", 24))
        peso_label.pack(pady=20)
        
        atualizar_peso()  
        root.mainloop()  
    except KeyboardInterrupt:
        print("Captura interrompida.")
    finally:
        sock.close()
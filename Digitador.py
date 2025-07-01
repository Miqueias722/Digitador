import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time
import keyboard
import os
import json
import webbrowser

class Configuracoes:
    def __init__(self):
        # aqui é o tempo que o programa espera antes de começar a digitar
        self.tempo_espera = 2
        # o tema da janela, pode ser escuro ou claro
        self.tema = 'Escuro'
        # a tecla que serve pra parar o que tá digitando
        self.tecla_parar = 'F3'
        # flag pra avisar se já falou o aviso ou não
        self.avisado = False
        # velocidade da digitação, padrão é normal
        self.velocidade = 'Padrão'

config = Configuracoes()

# pasta onde o programa guarda as config
appdata_dir = os.path.join(os.getenv('APPDATA'), 'Digitador')
os.makedirs(appdata_dir, exist_ok=True)
config_path = os.path.join(appdata_dir, 'config.json')

def carregar_config():
    # se existir arquivo de config, pega ele e coloca tudo no config
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            data = json.load(f)
            config.__dict__.update(data)

carregar_config()

# força voltar pra "Padrão" se for "Lenta"
if config.velocidade == "Lenta":
    config.velocidade = "Padrão"

def salvar_config():
    # salva as config atuais no arquivo
    with open(config_path, 'w') as f:
        json.dump(config.__dict__, f)

rodape_config = None
parar = False

def digitar_texto(texto):
    global parar
    # espera o tempo configurado antes de começar a digitar
    time.sleep(config.tempo_espera)

    # aqui define a velocidade de digitação de acordo com o que o usuário escolheu
    if config.velocidade == 'Rápido':
        velocidade = 0.05 # a velocidade rápida maioria das vezes n funciona pelo limite de caracteres por segundo do redação paraná
    else:  # padrão é meio rápido
        velocidade = 1 / 12 

    for char in texto:
        if parar:  # se apertar a tecla pra parar, sai do loop
            break
        if char not in ['\n', '\r']:  # ignora quando for tecla Enter
            keyboard.write(char, delay=velocidade)

    # volta a janela principal visível depois de digitar tudo
    root.deiconify()
    if hasattr(root, 'config_janela') and root.config_janela.winfo_exists():
        root.config_janela.deiconify()

def aplicar_tema_widget(widget):
    # escolhe a cor de fundo e texto dependendo do tema
    bg = "white" if config.tema == "Claro" else "#003b3b"
    fg = "black" if config.tema == "Claro" else "white"
    widget.configure(bg=bg)
    return bg, fg

def aplicar_tema_total():
    global rodape_config
    # aplica o tema em tudo da janela principal
    bg_color, fg_color = aplicar_tema_widget(root)
    main_frame.configure(bg=bg_color)
    texto_input.configure(
        bg="#004d4d" if config.tema == "Escuro" else "#eaffea",
        fg="white" if config.tema == "Escuro" else "black",
        insertbackground="white" if config.tema == "Escuro" else "black"
    )
    como_label.configure(bg=bg_color, fg="#00ffb3")
    instrucao_label.configure(bg=bg_color, fg=fg_color)
    rodape_main.configure(bg=bg_color, fg="#00ffb3", cursor="hand2")

    for frame in [botoes_frame, instrucoes_frame, texto_frame]:
        frame.configure(bg=bg_color)
        for widget in frame.winfo_children():
            if isinstance(widget, tk.Button):
                widget.configure(bg="#00ffb3", fg="black")
            elif isinstance(widget, tk.Label):
                widget.configure(bg=bg_color, fg=fg_color)

    # aplica o tema na janela de config se estiver aberta
    if hasattr(root, 'config_janela') and root.config_janela.winfo_exists():
        config_janela = root.config_janela
        config_janela.configure(bg=bg_color)
        for widget in config_janela.winfo_children():
            if isinstance(widget, tk.Frame):
                widget.configure(bg=bg_color)
                for child in widget.winfo_children():
                    try:
                        child.configure(bg=bg_color, fg=fg_color)
                    except:
                        pass
        if rodape_config and rodape_config.winfo_exists():
            rodape_config.configure(bg=bg_color, fg="#00ffb3", cursor="hand2")

def abrir_configuracoes():
    global rodape_config

    # se a janela de config já tá aberta, só mostra ela de novo
    if hasattr(root, 'config_janela') and root.config_janela.winfo_exists():
        root.config_janela.deiconify()
        return

    # cria a janela nova de config
    config_janela = tk.Toplevel(root)
    root.config_janela = config_janela
    config_janela.title("Configurações")
    config_janela.geometry("400x350")
    config_janela.minsize(400, 350)

    aplicar_tema_total()
    bg_color, fg_color = aplicar_tema_widget(config_janela)

    frame = tk.Frame(config_janela, bg=bg_color)
    frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

    config_janela.grid_rowconfigure(0, weight=1)
    config_janela.grid_columnconfigure(0, weight=1)

    # mostra qual tecla é pra parar a digitação
    label_f3 = tk.Label(frame, text=f"{config.tecla_parar}", font=("Arial", 13, "bold"), fg="black", bg="#00ffb3")
    label_f3.grid(row=0, column=0, sticky="ew", pady=(0, 2))

    tk.Label(frame, text="Essa tecla pausa a digitação automática.", bg=bg_color, fg=fg_color).grid(row=1, column=0, sticky="w", pady=(0, 8))

    def escolher_tecla():
        # abre uma janelinha pra escolher outra tecla pra parar digitação
        top = tk.Toplevel(config_janela)
        top.title("Pressione uma tecla")
        top.geometry("300x100")
        label = tk.Label(top, text="Pressione a tecla desejada para parar a digitação", font=("Arial", 10))
        label.pack(pady=20)
        top.focus_force()
        top.grab_set()

        def on_key_press(event):
            tecla = event.keysym.upper()
            if tecla == 'ESCAPE':
                top.destroy()
                return
            config.tecla_parar = tecla
            label_f3.config(text=f"{config.tecla_parar}")
            salvar_config()
            keyboard.clear_all_hotkeys()
            keyboard.add_hotkey(config.tecla_parar, parar_digitacao)
            top.destroy()

        top.bind("<Key>", on_key_press)

    tk.Button(frame, text="Alterar Tecla", command=escolher_tecla, bg="#00ffb3", fg="black", font=("Arial", 11, "bold"), height=2).grid(row=2, column=0, sticky="ew", pady=(0, 8))

    tk.Label(frame, text="Tempo de espera (segundos):", fg=fg_color, bg=bg_color).grid(row=3, column=0, sticky="w")
    tempo_entry = tk.Entry(frame)
    tempo_entry.insert(0, str(config.tempo_espera))
    tempo_entry.grid(row=4, column=0, sticky="ew", pady=(0, 8))
    tempo_entry.config(validate="key", validatecommand=(root.register(lambda P: P.replace('.','',1).isdigit() or P==""), '%P'))
    tempo_entry.bind("<KeyRelease>", lambda e: (config.__setattr__('tempo_espera', float(tempo_entry.get()) if tempo_entry.get().replace('.','',1).isdigit() else 2), salvar_config()))

    tk.Label(frame, text="Tema de Interface:", fg=fg_color, bg=bg_color).grid(row=5, column=0, sticky="w")
    tema_combo = ttk.Combobox(frame, values=["Escuro", "Claro"], state="readonly")
    tema_combo.set(config.tema)
    tema_combo.grid(row=6, column=0, sticky="ew", pady=(0, 8))
    tema_combo.bind("<<ComboboxSelected>>", lambda e: (config.__setattr__('tema', tema_combo.get()), salvar_config(), aplicar_tema_total()))

    tk.Label(frame, text="Velocidade de Digitação:", fg=fg_color, bg=bg_color).grid(row=7, column=0, sticky="w")
    velocidade_combo = ttk.Combobox(frame, values=["Rápido", "Padrão"], state="readonly")
    velocidade_combo.set(config.velocidade)
    velocidade_combo.grid(row=8, column=0, sticky="ew", pady=(0, 8))

    def ao_mudar_velocidade(e):
        # quando mudar a velocidade, avisa que rápido pode dar ruim no Redação Paraná
        nova = velocidade_combo.get()
        if nova == "Rápido":
            if not messagebox.askyesno("Aviso", "A opção 'Rápida' pode não ser aceita no Redação Paraná.\n\nA recomendada é 'Padrão'.\n\nDeseja continuar mesmo assim?"):
                velocidade_combo.set("Padrão")
                return
        config.velocidade = nova
        salvar_config()

    velocidade_combo.bind("<<ComboboxSelected>>", ao_mudar_velocidade)

    frame.grid_columnconfigure(0, weight=1)
    rodape_config = tk.Label(config_janela, text="Feito por Miqueias722", font=("Arial", 9, "bold"), fg="#00ffb3", bg=bg_color, cursor="hand2")
    rodape_config.grid(row=1, column=0, pady=5, sticky="s")
    rodape_config.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/miqueiasaquinoo/"))

def iniciar_digitacao():
    global parar
    # pega o texto que o usuário colocou
    texto = texto_input.get("1.0", "end-1c").rstrip()
    # se não tiver texto, avisa
    if not texto:
        messagebox.showwarning("Aviso", "Digite algum texto antes de iniciar.")
        return

    # se nunca avisou o aviso, mostra o aviso (pq a janela some e tem que escolher o lugar pra digitar)
    if not config.avisado:
        resposta = messagebox.askokcancel("Aviso", f"ATENÇÃO:\n\n- Pressionar {config.tecla_parar} irá PAUSAR a digitação automática.\n- As janelas serão minimizadas ao iniciar.\nVocê terá tempo para selecionar o campo onde será digitado.\n\nDeseja continuar?")
        if not resposta:
            return
        config.avisado = True
        salvar_config()

    parar = False
    # esconde a janela principal pra digitar sem atrapalhar
    root.iconify()
    if hasattr(root, 'config_janela') and root.config_janela.winfo_exists():
        root.config_janela.iconify()
    # começa a digitar numa thread separada
    threading.Thread(target=digitar_texto, args=(texto,), daemon=True).start()

def parar_digitacao():
    global parar
    # serve pra parar a digitação quando apertar a tecla
    parar = True

# configura o atalho da tecla parar
keyboard.add_hotkey(config.tecla_parar, parar_digitacao)

# cria a janela principal do app
root = tk.Tk()
root.title("Digitador Automático")
root.geometry("400x500")
root.minsize(400, 500)

main_frame = tk.Frame(root)
main_frame.grid(row=0, column=0, sticky="nsew")

root.grid_rowconfigure(0, weight=1)
root.grid_columnconfigure(0, weight=1)

texto_frame = tk.Frame(main_frame)
texto_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 5))

texto_input = tk.Text(texto_frame, font=("Arial", 12), wrap="word")
texto_input.pack(fill="both", expand=True)

botoes_frame = tk.Frame(main_frame)
botoes_frame.grid(row=1, column=0, sticky="ew", padx=10)

tk.Button(botoes_frame, text="🚀 Iniciar Digitação", command=iniciar_digitacao, font=("Arial", 12, "bold"), height=2, bg="#00ffb3", fg="black").pack(side="left", expand=True, fill="x", padx=5, pady=5)
tk.Button(botoes_frame, text="⚙️ Configurações", command=abrir_configuracoes, font=("Arial", 12, "bold"), height=2, bg="#00ffb3", fg="black").pack(side="left", expand=True, fill="x", padx=5, pady=5)

instrucoes_frame = tk.Frame(main_frame)
instrucoes_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(5, 5))

como_label = tk.Label(instrucoes_frame, text="+ Como usar:", font=("Arial", 10, "bold"), anchor="w", justify="left")
como_label.pack(anchor="w")

instrucao_label = tk.Label(instrucoes_frame, text="1. Cole seu texto na área acima\n2. Clique no foguete\n3. Posicione o cursor\n4. Espere o tempo configurado", font=("Arial", 9), justify="left")
instrucao_label.pack(anchor="w")

rodape_main = tk.Label(root, text="Feito por Miqueias722", font=("Arial", 9, "bold"), fg="#00ffb3", cursor="hand2")
rodape_main.grid(row=1, column=0, pady=5, sticky="s")
rodape_main.bind("<Button-1>", lambda e: webbrowser.open("https://www.instagram.com/miqueiasaquinoo/"))

main_frame.grid_rowconfigure(0, weight=1)
main_frame.grid_rowconfigure(1, weight=0)
main_frame.grid_rowconfigure(2, weight=0)
main_frame.grid_columnconfigure(0, weight=1)

aplicar_tema_total()
root.mainloop()

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import csv
from .logic import adicionar_transacao
from .storage import carregar_dados, salvar_dados

# Função para atualizar a interface com os dados mais recentes
def atualizar_interface(dados, tree, lbl_saldo, entry_data_de, entry_data_ate):
    # Limpa os dados da interface (a lista de transações na treeview)
    for row in tree.get_children():
        tree.delete(row)

    transacoes = filtrar_transacoes(dados, entry_data_de, entry_data_ate)

    for t in transacoes:
        cor = "receita" if t["tipo"] == "receita" else "despesa"
        tree.insert("", "end", values=(t["data"], t["tipo"], f"R$ {t['valor']:.2f}", t["descricao"]), tags=(cor,))

    saldo = sum(t["valor"] if t["tipo"] == "receita" else -t["valor"] for t in transacoes)
    lbl_saldo["text"] = f"Saldo do Período: R$ {saldo:.2f}"
    lbl_saldo["fg"] = "#3cba54" if saldo >= 0 else "#db3236"

# Função para filtrar as transações com base nas datas
def filtrar_transacoes(dados, entry_data_de, entry_data_ate):
    data_de_str = entry_data_de.get().strip()
    data_ate_str = entry_data_ate.get().strip()

    try:
        data_de = datetime.strptime(data_de_str, "%d/%m/%Y") if data_de_str else None
        data_ate = datetime.strptime(data_ate_str, "%d/%m/%Y") if data_ate_str else None
    except ValueError:
        messagebox.showerror("Erro", "Datas inválidas. Use o formato dd/mm/aaaa.")
        return []

    transacoes_filtradas = []
    for t in dados["transacoes"]:
        data_t = datetime.strptime(t["data"], "%d/%m/%Y %H:%M")
        if data_de and data_t < data_de:
            continue
        if data_ate and data_t > data_ate:
            continue
        transacoes_filtradas.append(t)
    return transacoes_filtradas

# Função para limpar dados e reiniciar o controle financeiro
def novo_controle(dados, tree, lbl_saldo, entry_data_de, entry_data_ate):
    if messagebox.askyesno("Novo Controle", "Tem certeza que deseja apagar todos os dados?"):
        dados["transacoes"] = []  # Limpa as transações
        salvar_dados(dados)  # Salva os dados atualizados
        atualizar_interface(dados, tree, lbl_saldo, entry_data_de, entry_data_ate)  # Atualiza a interface com dados limpos

# Função principal de interface
def iniciar_interface():
    dados = carregar_dados()  # Carrega os dados de transações iniciais

    root = tk.Tk()
    root.title("Controle Financeiro")
    root.geometry("750x500")
    root.configure(bg="#f0f0f0")

    # Formulário de entrada
    frame_form = tk.Frame(root, bg="#f0f0f0")
    frame_form.pack(pady=10)

    tk.Label(frame_form, text="Valor (R$):", bg="#f0f0f0").grid(row=0, column=0, padx=5)
    entry_valor = tk.Entry(frame_form)
    entry_valor.grid(row=0, column=1)

    tk.Label(frame_form, text="Descrição:", bg="#f0f0f0").grid(row=0, column=2, padx=5)
    entry_desc = tk.Entry(frame_form, width=30)
    entry_desc.grid(row=0, column=3)

    # Filtros por data
    tk.Label(frame_form, text="De (dd/mm/aaaa):", bg="#f0f0f0").grid(row=2, column=0, padx=5)
    entry_data_de = tk.Entry(frame_form, width=12)
    entry_data_de.grid(row=2, column=1)

    tk.Label(frame_form, text="Até:", bg="#f0f0f0").grid(row=2, column=2, padx=5)
    entry_data_ate = tk.Entry(frame_form, width=12)
    entry_data_ate.grid(row=2, column=3)

    # Lista de transações
    columns = ("data", "tipo", "valor", "descricao")
    tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
    tree.heading("data", text="Data")
    tree.heading("tipo", text="Tipo")
    tree.heading("valor", text="Valor")
    tree.heading("descricao", text="Descrição")
    tree.pack(pady=10)

    tree.tag_configure("receita", foreground="green")
    tree.tag_configure("despesa", foreground="red")

    # Saldo
    lbl_saldo = tk.Label(root, text="Saldo: R$ 0.00", font=("Arial", 14), bg="#f0f0f0")
    lbl_saldo.pack()

    # Função para adicionar transações
    def adicionar(tipo):
        try:
            valor = float(entry_valor.get())
        except ValueError:
            messagebox.showerror("Erro", "Insira um valor numérico válido.")
            return

        descricao = entry_desc.get().strip()
        if not descricao:
            messagebox.showerror("Erro", "Insira uma descrição.")
            return

        adicionar_transacao(dados, tipo, valor, descricao)
        entry_valor.delete(0, tk.END)
        entry_desc.delete(0, tk.END)
        atualizar_interface(dados, tree, lbl_saldo, entry_data_de, entry_data_ate)

    # Botões da interface
    frame_botoes = tk.Frame(root, bg="#f0f0f0")
    frame_botoes.pack(pady=5)

    tk.Button(frame_botoes, text="➕ Receita", width=15, bg="#d4f4dd", command=lambda: adicionar("receita")).grid(row=0, column=0, padx=5)
    tk.Button(frame_botoes, text="➖ Despesa", width=15, bg="#f4d4d4", command=lambda: adicionar("despesa")).grid(row=0, column=1, padx=5)
    tk.Button(frame_botoes, text="🔍 Filtrar", width=15, bg="#e0e0e0", command=lambda: atualizar_interface(dados, tree, lbl_saldo, entry_data_de, entry_data_ate)).grid(row=0, column=2, padx=5)

    # Função para exportar para CSV
    def exportar_csv():
        transacoes = filtrar_transacoes(dados, entry_data_de, entry_data_ate)
        if not transacoes:
            messagebox.showinfo("Aviso", "Nenhuma transação encontrada no período.")
            return

        caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if caminho:
            with open(caminho, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["Data", "Tipo", "Valor", "Descrição"])
                for t in transacoes:
                    writer.writerow([t["data"], t["tipo"], f"{t['valor']:.2f}", t["descricao"]])
            messagebox.showinfo("Sucesso", f"Relatório exportado para:\n{caminho}")

    btn_exportar = tk.Button(root, text="📤 Exportar CSV", bg="#c7dfff", command=exportar_csv)
    btn_exportar.pack(pady=10)

    # Novo Controle
    btn_resetar = tk.Button(root, text="🗑️ Novo Controle", bg="#ffd6d6", command=lambda: novo_controle(dados, tree, lbl_saldo, entry_data_de, entry_data_ate))
    btn_resetar.pack(pady=5)

    # Atualiza a interface com os dados carregados
    atualizar_interface(dados, tree, lbl_saldo, entry_data_de, entry_data_ate)
    root.mainloop()
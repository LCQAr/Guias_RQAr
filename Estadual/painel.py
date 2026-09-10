"""
painel.py

Interface simples com botao para rodar a atualizacao do livro, sem
precisar usar o terminal no dia a dia. Usa apenas Tkinter, que ja vem
junto com o Python -- nao precisa instalar nada a mais para isso.

COMO ABRIR
----------
Windows: duplo clique em "Abrir Painel.bat"
Mac:     duplo clique em "Abrir Painel.command"

(Esses arquivos so chamam este script por baixo dos panos.)
"""

import os
import subprocess
import sys
import threading
from pathlib import Path

import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk

HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output"

UFS = [
    "AC", "AL", "AP", "AM", "BA", "CE", "DF", "ES", "GO", "MA", "MT", "MS",
    "MG", "PA", "PB", "PR", "PE", "PI", "RJ", "RN", "RS", "RO", "RR", "SC",
    "SP", "SE", "TO",
]


class Painel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Guia RQAr Estadual — Painel de Atualização")
        self.geometry("640x480")
        self.resizable(True, True)

        tk.Label(
            self, text="Atualização do Guia RQAr Estadual",
            font=("Segoe UI", 14, "bold"),
        ).pack(pady=(16, 4))

        tk.Label(
            self,
            text="Clique no botão abaixo para recalcular tabelas, mapas e números,\n"
                 "e gerar uma nova versão do livro em Word e PDF.",
            font=("Segoe UI", 10), justify="center",
        ).pack(pady=(0, 12))

        seletor_frame = tk.Frame(self)
        seletor_frame.pack(pady=(0, 12))
        tk.Label(seletor_frame, text="Estado (UF):", font=("Segoe UI", 10, "bold")).pack(side="left", padx=(0, 8))
        self.uf_var = tk.StringVar(value="SC")
        self.uf_combo = ttk.Combobox(
            seletor_frame, textvariable=self.uf_var, values=UFS,
            state="readonly", width=6, font=("Segoe UI", 10),
        )
        self.uf_combo.pack(side="left")

        self.botao_rodar = tk.Button(
            self, text="▶  Atualizar Livro Agora", font=("Segoe UI", 12, "bold"),
            bg="#2C3E50", fg="white", activebackground="#34495E", activeforeground="white",
            padx=20, pady=10, command=self.rodar_build,
        )
        self.botao_rodar.pack(pady=(0, 12))

        self.log = scrolledtext.ScrolledText(
            self, height=16, font=("Consolas", 9), state="disabled", bg="#1E1E1E", fg="#D4D4D4",
        )
        self.log.pack(fill="both", expand=True, padx=16, pady=(0, 12))

        botoes_frame = tk.Frame(self)
        botoes_frame.pack(pady=(0, 16))

        self.botao_pasta = tk.Button(
            botoes_frame, text="📂 Abrir pasta de resultados",
            command=self.abrir_pasta_resultados, state="disabled",
        )
        self.botao_pasta.pack(side="left", padx=6)

        self.botao_docx = tk.Button(
            botoes_frame, text="📄 Abrir livro (Word)",
            command=self.abrir_docx, state="disabled",
        )
        self.botao_docx.pack(side="left", padx=6)

    def escrever_log(self, texto):
        self.log.configure(state="normal")
        self.log.insert("end", texto)
        self.log.see("end")
        self.log.configure(state="disabled")

    def rodar_build(self):
        self.botao_rodar.configure(state="disabled", text="⏳ Atualizando... aguarde")
        self.uf_combo.configure(state="disabled")
        self.botao_pasta.configure(state="disabled")
        self.botao_docx.configure(state="disabled")
        self.log.configure(state="normal")
        self.log.delete("1.0", "end")
        self.log.configure(state="disabled")
        threading.Thread(target=self._rodar_build_thread, daemon=True).start()

    def _rodar_build_thread(self):
        try:
            python_exe = sys.executable
            env = os.environ.copy()
            env["GUIA_UF"] = self.uf_var.get()
            processo = subprocess.Popen(
                [python_exe, str(HERE / "build_book.py")],
                cwd=str(HERE),
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, bufsize=1, env=env,
            )
            for linha in processo.stdout:
                self.after(0, self.escrever_log, linha)
            processo.wait()

            if processo.returncode == 0:
                self.after(0, self.escrever_log, "\n✅ Concluído com sucesso!\n")
                self.after(0, self._habilitar_botoes_resultado)
            else:
                self.after(0, self.escrever_log, f"\n❌ Processo terminou com erro (código {processo.returncode}).\n")
                self.after(0, lambda: messagebox.showerror(
                    "Erro na atualização",
                    "Algo deu errado durante a atualização. Veja o registro na janela para detalhes.",
                ))
        except Exception as e:
            self.after(0, self.escrever_log, f"\n❌ Erro inesperado: {e}\n")
        finally:
            self.after(0, lambda: self.botao_rodar.configure(
                state="normal", text="▶  Atualizar Livro Agora"))
            self.after(0, lambda: self.uf_combo.configure(state="readonly"))

    def _habilitar_botoes_resultado(self):
        if OUTPUT_DIR.exists():
            self.botao_pasta.configure(state="normal")
        if (OUTPUT_DIR / "book_filled.docx").exists():
            self.botao_docx.configure(state="normal")

    def abrir_pasta_resultados(self):
        self._abrir_caminho(OUTPUT_DIR)

    def abrir_docx(self):
        self._abrir_caminho(OUTPUT_DIR / "book_filled.docx")

    def _abrir_caminho(self, caminho: Path):
        try:
            if sys.platform == "win32":
                subprocess.run(["explorer", str(caminho)])
            elif sys.platform == "darwin":
                subprocess.run(["open", str(caminho)])
            else:
                subprocess.run(["xdg-open", str(caminho)])
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível abrir: {e}")


if __name__ == "__main__":
    app = Painel()
    app.mainloop()
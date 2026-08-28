#!/usr/bin/python

import errno
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
import os
import signal
import socket
import sys
from time import sleep
from types import FrameType


class Server:
    """Servidor HTTP simplificado, para servir arquivos em rede local."""

    def __init__(self, port=8080):
        self.port = port
        self.server: ThreadingHTTPServer | None = None
        self.running = True

    def local_ip(self) -> str | None:
        """
        Tenta encontrar o ip da máquina na rede local.
        Retorna None quando não conseguir conexão com DNS externo.
        """

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.settimeout(3)
                s.connect(('8.8.8.8', 80))
                return s.getsockname()[0]
        except Exception:
            return None

    def register_signals(self):
        """Registra o handler para o desligamento do servidor."""

        signal.signal(signal.SIGINT, self.shutdown_handler)
        signal.signal(signal.SIGTERM, self.shutdown_handler)

    def shutdown_handler(self, sig: int, frame: FrameType | None):
        """Handler para desligamento do servidor."""

        sig_name = 'SIGINT (Ctrl+C)' if sig == signal.SIGINT else 'SIGTERM (kill)'
        print(f'\n📢 Recebido {sig_name}')
        self.shutdown_server()

    def shutdown_server(self):
        """Procede o desligamento do server."""

        if not self.running:
            return

        self.running = False
        print('🛑 Encerrando servidor...')

        if self.server:
            print('⏳ Aguardando finalização de requisições...')
            sleep(1)

            print('🔌 Fechando conexões...')
            self.server.shutdown()
            self.server.server_close()

        print('✅ Servidor finalizado com sucesso!')
        sys.exit(0)

    def start_server(self):
        """Inicia o servidor."""

        self.register_signals()

        print("🔄 INICIANDO SERVIDOR...")
        print(f"📁 Diretório: {os.getcwd()}")

        if ip := self.local_ip():
            print(f'🌐 Endereço de acesso: http://{ip}:{self.port}')
        else:
            print('🌐 Não foi possível detectar o IP automaticamente.')
            print(f'   💡 Acesse via: http://<SEU_IP>:{self.port}')
            print('   💡 Descubra seu IP:')
            print('      • No Linux: ip addr')
            print('      • No Windows: ipconfig')

        try:
            self.server = ThreadingHTTPServer(
                ('', self.port), SimpleHTTPRequestHandler
            ).serve_forever()

            print('🚀 SERVIDOR RODANDO!', end='\n\n')
            self.server.serve_forever()

        except OSError as e:
            if e.errno == errno.EADDRINUSE:
                print(f'\n❌ Erro: Porta {self.port} já está em uso!')
                print('💡 Use outra porta ou encerre o processo que está usando-a.')
            else:
                print(f'\n❌ Erro ao iniciar servidor: {e}')
                sys.exit(1)

        except KeyboardInterrupt:
            self.shutdown_server()

        except Exception as e:
            print(f'\n❌ Erro inesperado: {e}')
            self.shutdown_server()


if __name__ == '__main__':
    server = Server(port=8080)
    server.start_server()

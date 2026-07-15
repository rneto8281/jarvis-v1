import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.ServerSocket;
import java.net.Socket;

/**
 * EchoService
 *
 * Serviço auxiliar de exemplo, demonstrando o padrão de integração
 * entre o backend Python do JarvisAI e serviços Java desacoplados.
 *
 * Este serviço apenas ecoa mensagens recebidas via socket TCP na porta
 * 9090. Serve como esqueleto para futuros serviços reais (ex.:
 * monitoramento de dispositivos, processamento paralelo em lote).
 */
public final class EchoService {

    private static final int PORTA = 9090;

    public static void main(String[] args) throws IOException {
        try (ServerSocket servidor = new ServerSocket(PORTA)) {
            System.out.println("EchoService do JarvisAI ouvindo na porta " + PORTA);

            while (true) {
                try (Socket cliente = servidor.accept()) {
                    tratarCliente(cliente);
                }
            }
        }
    }

    /**
     * Lê uma linha do cliente conectado e devolve a mesma mensagem,
     * prefixada para indicar que passou pelo serviço Java.
     */
    private static void tratarCliente(Socket cliente) throws IOException {
        BufferedReader entrada = new BufferedReader(
                new InputStreamReader(cliente.getInputStream()));
        PrintWriter saida = new PrintWriter(cliente.getOutputStream(), true);

        String mensagem = entrada.readLine();
        if (mensagem != null) {
            saida.println("[java-service] " + mensagem);
        }
    }

    private EchoService() {
        // Classe utilitária: não deve ser instanciada.
    }
}

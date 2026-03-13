package com.example;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import java.time.ZonedDateTime;
import java.net.InetAddress;
import java.net.UnknownHostException;

@Path("/")
public class DemoResource {

    @GET
    @Produces(MediaType.APPLICATION_JSON)
    public Response hello() throws UnknownHostException {
        return new Response(
            "Hello from Java (Quarkus) - Optimized for Firecracker",
            ZonedDateTime.now().toString(),
            InetAddress.getLocalHost().getHostName()
        );
    }

    @GET
    @Path("/health")
    @Produces(MediaType.TEXT_PLAIN)
    public String health() {
        return "OK";
    }

    public static class Response {
        public String message;
        public String timestamp;
        public String host;

        public Response(String message, String timestamp, String host) {
            this.message = message;
            this.timestamp = timestamp;
            this.host = host;
        }
    }
}

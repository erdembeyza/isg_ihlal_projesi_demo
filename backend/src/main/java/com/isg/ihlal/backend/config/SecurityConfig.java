package com.isg.ihlal.backend.config;

import com.isg.ihlal.backend.security.JwtAuthenticationFilter;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpStatus;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;
import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;
import org.springframework.web.cors.CorsConfiguration;
import org.springframework.web.cors.CorsConfigurationSource;
import org.springframework.web.cors.UrlBasedCorsConfigurationSource;

import java.util.Arrays;
import java.util.List;

/**
 * MODUL-3 (tasarim_mimari.md): Spring Security'nin varsayilan (formLogin +
 * rastgele uretilmis sifre) davranisini kapatip, tamamen stateless (session'siz)
 * JWT tabanli bir guvenlik zinciri kurar.
 * <p>
 * - /api/auth/login herkese acik (henuz token yok, giris burada aliniyor).
 * - Diger tum /api/** uclari kimlik dogrulama ister; rol bazli kisitlar
 *   endpoint bazinda @PreAuthorize("hasRole('ISG_YONETICI')") gibi
 *   anotasyonlarla Faz 4'te eklenecek (bkz. @EnableMethodSecurity).
 */
@Configuration
@EnableWebSecurity
@EnableMethodSecurity
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthenticationFilter;
    private final List<String> corsAllowedOrigins;

    public SecurityConfig(
            JwtAuthenticationFilter jwtAuthenticationFilter,
            @Value("${app.cors-allowed-origins}") String corsAllowedOrigins
    ) {
        this.jwtAuthenticationFilter = jwtAuthenticationFilter;
        this.corsAllowedOrigins = Arrays.stream(corsAllowedOrigins.split(","))
                .map(String::trim)
                .filter(s -> !s.isEmpty())
                .toList();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }

    @Bean
    public AuthenticationManager authenticationManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public SecurityFilterChain securityFilterChain(HttpSecurity http) throws Exception {
        http
                // REST API + JWT: CSRF korumasi cerez tabanli session'lar icin anlamlidir,
                // burada session olmadigi (STATELESS) icin gerek yok.
                .csrf(csrf -> csrf.disable())
                .cors(cors -> cors.configurationSource(corsConfigurationSource()))
                .sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS))
                .authorizeHttpRequests(auth -> auth
                        .requestMatchers("/api/auth/login").permitAll()
                        .requestMatchers("/api/auth/**").authenticated()
                        // Spring Boot'ta response.sendError(...) cagirimi sunucu icinde /error'a
                        // forward eder; bu forward guvenlik zincirinden TEKRAR gecer ve JWT filtresi
                        // (OncePerRequestFilter oldugu icin) ikinci kez calismaz. /error permitAll
                        // olmazsa bu ikinci gecis "kimliksiz" sayilir ve orijinal 403 yerine 401
                        // donmesine (yanlis status code) neden olur.
                        .requestMatchers("/error").permitAll()
                        .anyRequest().authenticated()
                )
                .exceptionHandling(ex -> ex
                        // Kimliksiz erisim -> 401 (403 yerine), token hic yok/gecersiz demek.
                        .authenticationEntryPoint((request, response, authException) ->
                                response.sendError(HttpStatus.UNAUTHORIZED.value(), "Kimlik dogrulama gerekli"))
                        // Kimlik dogru ama rolu yetersiz -> 403.
                        .accessDeniedHandler((request, response, accessDeniedException) ->
                                response.sendError(HttpStatus.FORBIDDEN.value(), "Bu islem icin yetkiniz yok"))
                )
                .addFilterBefore(jwtAuthenticationFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    /**
     * Angular gelistirme sunucusu (ng serve, localhost:4200) farkli bir origin
     * oldugu icin tarayici CORS ile korur; bu yapilandirma olmadan Angular'dan
     * atilan istekler tarayici tarafinda bloklanir. Uretimde Angular build
     * ciktisi ayni origin'den (backend'in statik dosya sunumu ya da reverse
     * proxy ile) servis edilirse bu ayara gerek kalmaz.
     */
    @Bean
    public CorsConfigurationSource corsConfigurationSource() {
        CorsConfiguration config = new CorsConfiguration();
        config.setAllowedOrigins(corsAllowedOrigins);
        config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
        config.setAllowedHeaders(List.of("*"));
        config.setAllowCredentials(true);

        UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
        source.registerCorsConfiguration("/**", config);
        return source;
    }
}

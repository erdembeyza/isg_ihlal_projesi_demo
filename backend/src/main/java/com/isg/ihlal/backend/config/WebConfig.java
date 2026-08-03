package com.isg.ihlal.backend.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.ResourceHandlerRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;

import java.nio.file.Paths;

/**
 * FileStorageService ile diske yazilan ihlal kanit fotograflarini
 * "/uploads/**" altindan statik dosya olarak sunar.
 * <p>
 * Not: Bu path SecurityConfig'deki "anyRequest().authenticated()" kuralina
 * tabidir, yani fotograflara erismek icin de gecerli bir JWT gerekir.
 */
@Configuration
public class WebConfig implements WebMvcConfigurer {

    private final String uploadDir;

    public WebConfig(@Value("${app.upload-dir}") String uploadDir) {
        this.uploadDir = uploadDir;
    }

    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        String kokDizinUri = Paths.get(uploadDir).toAbsolutePath().normalize().toUri().toString();
        registry.addResourceHandler("/uploads/**")
                .addResourceLocations(kokDizinUri);
    }
}

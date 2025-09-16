@Configuration
@EnableWebMvc
@OpenAPIDefinition(
    info = @Info(
        title = "${PROJECT_NAME}",
        version = "1.0.0",
        description = "${PROJECT_DESCRIPTION}",
        contact = @Contact(
            name = "${COMPANY_NAME}",
            email = "support@${COMPANY_DOMAIN}"
        )
    )
)
public class OpenApiConfig implements WebMvcConfigurer {
    @Override
    public void addResourceHandlers(ResourceHandlerRegistry registry) {
        registry.addResourceHandler("/swagger-ui/**")
                .addResourceLocations("classpath:/META-INF/resources/webjars/springdoc-openapi-ui/")
                .resourceChain(false);
    }
}

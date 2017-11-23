library(xml2)
library(dplyr)
library(rvest)
# reading the data
hoy_fb_url <- "https://raw.githubusercontent.com/Pedromoisescamacho/periodicos-dominicanos/master/datasets_noticias/hoy_fb.csv"
hoy_df <- read.csv(hoy_fb_url, stringsAsFactors = F)
hoy_url <- hoy_df$url
noticia <- read_html("http://hoy.com.do/monsenor-benito-angeles-encabezara-el-segundo-encuentro-de-pan-y-vino-en-punta-cana/")
contenido <- noticia %>% html_nodes(".single-article-title") %>% html_text


contenido <- function(url){
        content <- function(url){
                noticia <- read_html(url)
                contenido <- noticia %>% html_nodes("#single-article-main-content p") %>% html_text %>% as.list() %>% do.call(what = paste)
                contenido <- ifelse(identical(contenido, character(0)), "NULL", contenido)
                contenido
        }
        return(tryCatch(content(url), error = function(e) "NULL"))
}


fecha <- function(url){
        fecha <- function(url){
                noticia <- read_html(url)
                fecha <- noticia %>% html_nodes("#single-article-section p:nth-child(1) strong") %>% html_text
                fecha <- ifelse(identical(fecha, character(0)), "NULL", fecha)
                fecha
        }
        return(tryCatch(fecha(url), error = function(e) "NULL"))
}

titulo <- function(url){
        title <- function(url){
                noticia <- read_html(url)
                title <- noticia %>% html_nodes(".single-article-title") %>% html_text
                title <- ifelse(identical(title, character(0)), "NULL", title)
                title
        }
        return(tryCatch(title(url), error = function(e) "NULL"))
}

#extraer los elementos para todos los URL
content <- c()
for (url in hoy_url[1:4]){
        cont <- contenido(url)
        content <- c(content, cont)
}

contenidos <- sapply(hoy_url, contenido)
fechas <- sapply(hoy_url, fecha)
titulos <- sapply(hoy_url, titulo)

noticias <- data.frame(contenidos, fechas, titulos, stringsAsFactors = F)
write.csv(noticias, "./noticias csv/hoy_noticias.csv")

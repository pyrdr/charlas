library(xml2)
library(dplyr)
library(rvest)
# reading the data
na_fb_url <- "https://raw.githubusercontent.com/Pedromoisescamacho/periodicos-dominicanos/master/datasets_noticias/fb_nacional.csv"
na_df <- read.csv(na_fb_url, stringsAsFactors = F)
na_url <- na_df$url
noticia <- read_html("http://ow.ly/oaKb30fLgDJ")
contenido <- noticia %>% html_nodes(".category-noticias-ultimo-minuto h2") %>% html_text

contenido <- function(url){
        content <- function(url){
                noticia <- read_html(url)
                contenido <- noticia %>% html_nodes(".post-text p") %>% html_text %>% 
                        as.list() %>% do.call(what = paste)
                contenido <- ifelse(identical(contenido, character(0)), "NULL", contenido)
                contenido
        }
        return(tryCatch(content(url), error = function(e) "NULL"))
}


fecha <- function(url){
        fecha <- function(url){
                noticia <- read_html(url)
                fecha <- noticia %>% html_nodes(".meta-item-details:nth-child(2)") %>% html_text 
                fecha <- ifelse(identical(fecha, character(0)), "NULL", fecha)
                fecha
        }
        return(tryCatch(fecha(url), error = function(e) "NULL"))
}

titulo <- function(url){
        title <- function(url){
                noticia <- read_html(url)
                title <- noticia %>% html_nodes(".category-noticias-ultimo-minuto h2") %>% html_text
                title <- ifelse(identical(title, character(0)), "NULL", title)
                title
        }
        return(tryCatch(title(url), error = function(e) "NULL"))
}


content <- c()
for (url in na_url[1:14]){
        cont <- contenido(url)
        content <- c(content, cont)
}
contenidos <- sapply(na_url, contenido)
contenidos[sapply(contenidos, is.null)] <- "NULL"
contenidos_v <- c(unlist(contenidos))


fechas <- sapply(na_url, fecha)
fechas[sapply(fechas, is.null)] <- "NULL"
fechas[]
fechas_v <- c(unlist(fechas))

titulos <- sapply(na_url, titulo)
titulos[sapply(titulos, is.null)] <- "NULL"
titulos_v <- c(unlist(titulos))


fechas[sapply(fechas, is.null)] <- "NA"

noticias <- data.frame(contenidos, fechas, titulos, stringsAsFactors = F)
write.csv(noticias, "./noticias csv/nacional_noticias.csv")

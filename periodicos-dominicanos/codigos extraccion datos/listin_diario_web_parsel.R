library(xml2)
library(dplyr)
library(rvest)
# reading the data
ld_fb_url <- "https://raw.githubusercontent.com/Pedromoisescamacho/periodicos-dominicanos/master/datasets_noticias/fb_listin.csv"
ld_df <- read.csv(ld_fb_url, stringsAsFactors = F)
ld_url <- ld_df$url
noticia <- read_html(ld_url[7])
conte <- noticia %>% html_nodes(".art_sly_1 span") %>% html_text


contenido <- function(url){
        content <- function(url){
                noticia <- read_html(url)
                contenido <- noticia %>% html_nodes("#ArticleBody") %>% html_text %>% as.list() %>% do.call(what = paste)
                contenido <- ifelse(identical(contenido, character(0)), "NULL", contenido)
                contenido
        }
        return(tryCatch(content(url), error = function(e) "NULL"))
}

titulo <- function(url){
        title <- function(url){
                noticia <- read_html(url)
                title <- noticia %>% html_nodes(".art_titulo") %>% html_text 
                title <- ifelse(identical(title, character(0)), "NULL", title)
                title
        }
        return(tryCatch(title(url), error = function(e) "NULL"))
}

fecha <- function(url){
        date <- function(url){
                noticia <- read_html(url)
                pattern <- "[a-z].*[0-9]"
                fecha_cruda <- noticia %>% html_nodes(".art_sly_1 span") %>% html_text 
                fecha <- regmatches(fecha_cruda, regexpr(pattern, fecha_cruda)) #%>%  as.POSIXct(format = "%d %b %Y, %H:%M %p")
                fecha <- ifelse(identical(fecha, character(0)), "NULL", fecha)
                fecha
        }
        return(tryCatch(date(url), error = function(e) "NULL"))
}


content <- c()
for (url in ld_url){
        cont <- contenido(url)
        content <- c(content, cont)
}

contenidos <- sapply(ld_url, contenido)
titulos <- sapply(ld_url, titulo)
fechas <- sapply(ld_url, fecha)
fechas[sapply(fechas, is.null)] <- "NULL"
fechas2 <- fechas %>% unlist() %>% c()


noticias <- data.frame(contenidos, fechas2, titulos, stringsAsFactors = F)
write.csv(noticias, "./noticias csv/listin_diario_noticias.csv")

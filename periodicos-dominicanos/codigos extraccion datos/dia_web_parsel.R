library(xml2)
library(dplyr)
library(rvest)
# reading the data
dia_fb_url <- "https://raw.githubusercontent.com/Pedromoisescamacho/periodicos-dominicanos/master/datasets_noticias/fb_el_dia.csv"
dia_df <- read.csv(dia_fb_url, stringsAsFactors = F)
dia_url <- dia_df$url
noticia <- read_html(dia_url[50])
contenido <- noticia %>% html_nodes(".custom-column small") %>% html_text

contenido <- function(url){
        content <- function(url){
                noticia <- read_html(url)
                contenido <- noticia %>% html_nodes(".section-main-article section p") %>% html_text %>% 
                        as.list() %>% do.call(what = paste)
                contenido <- ifelse(identical(contenido, character(0)), "NULL", contenido)
                contenido
        }
        return(tryCatch(content(url), error = function(e) "NULL"))
}


fecha <- function(url){
        fecha <- function(url){
                noticia <- read_html(url)
                pattern <- "[0-9].*m"
                fecha_cruda <- noticia %>% html_nodes(".custom-column small") %>% html_text
                fecha <- regmatches(fecha_cruda, regexpr(pattern, fecha_cruda)) #%>%  as.POSIXct(format = "%d %b %Y, %H:%M %p")
                fecha <- ifelse(identical(fecha, character(0)), "NULL", fecha)
                fecha
        }
        return(tryCatch(fecha(url), error = function(e) "NA"))
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


content <- c()
for (url in dia_url[1:14]){
        cont <- contenido(url)
        content <- c(content, cont)
}

contenidos <- sapply(dia_url, contenido)
fechas <- sapply(dia_url, fecha)
titulos <- sapply(dia_url, titulo)

#putting the dataframe together
contenidos_v <- c(unlist(contenidos))
fechas_v <- c(unlist(fechas))

noticias <- data.frame(contenidos, fechas, titulos, stringsAsFactors = F)
write.csv(noticias, "./noticias csv/dia_noticias.csv")

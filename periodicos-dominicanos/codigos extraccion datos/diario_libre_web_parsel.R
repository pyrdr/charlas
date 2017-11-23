library(xml2)
library(dplyr)
library(rvest)
# reading the data
dl_fb_url <- "https://raw.githubusercontent.com/Pedromoisescamacho/periodicos-dominicanos/master/datasets_noticias/diario_libre_fb.csv"
dl_df <- read.csv(dl_fb_url, stringsAsFactors = F)
dl_url <- dl_df$url

#functions to extract information

noticia <- function(url){
        noticia <- read_html(url)
        #titulo <- noticia %>% html_nodes("title") %>% html_text
        contenido <- noticia %>% html_nodes("#layout-column_column-4 p") %>% html_text %>% 
                as.list() %>% do.call(what = paste)
        contenido <- ifelse(identical(contenido, character(0)), "NULL", contenido)
        pattern <- "[0-9].*M"
        fecha_cruda <- noticia %>% html_nodes(".art-date") %>% html_text
        fecha <- regmatches(fecha_cruda, regexpr(pattern, fecha_cruda)) #%>%  as.POSIXct(format = "%d %b %Y, %H:%M %p")
        #autor_crudo <- noticia %>% html_nodes("#layout-column_column-2 a") %>% html_text()
        #autor <- autor_crudo[autor_crudo != ""] 
        #resumen <- noticia %>% html_nodes(".art-sub") %>% html_text ###algunas noticias no tienen esto
        data.frame(contenido, fecha, stringsAsFactors = FALSE)
}

contenido <- function(url){
        content <- function(url){
                noticia <- read_html(url)
                contenido <- noticia %>% html_nodes("#layout-column_column-4 p") %>% html_text %>% 
                        as.list() %>% do.call(what = paste)
                #contenido <- ifelse(identical(contenido, character(0)), "NULL", contenido)
                contenido
        }
        return(tryCatch(content(url), error = function(e) "NULL"))
}

titulo <- function(url){
        title <- function(url){
                noticia <- read_html(url)
                title <- noticia %>% html_nodes("title") %>% html_text %>% 
                        as.list() %>% do.call(what = paste)
                title <- ifelse(identical(title, character(0)), "NULL", title)
                title
        }
        return(tryCatch(title(url), error = function(e) "NULL"))
}

fecha <- function(url){
        title <- function(url){
                noticia <- read_html(url)
                pattern <- "[0-9].*M"
                fecha_cruda <- noticia %>% html_nodes(".art-date") %>% html_text %>% gsub(pattern = ".*([0-9].{15,}M).*$","\\1", replacement = "\\1")
                #fecha <-  as.POSIXct(format = "%d %b %Y, %H:%M %p")
                #fecha <- ifelse(identical(fecha, character(0)), "NULL", fecha)
                #fecha
                fecha_cruda
        }
        return(tryCatch(title(url), error = function(e) "NULL"))
}


autor <- function(url){
        noticia <- read_html(url)
        autor_crudo <- noticia %>% html_nodes("#layout-column_column-2 a") %>% html_text()
        autor <- autor_crudo[autor_crudo != ""] 
        autor
}

#functions to extrac information for each url

contenidos <- sapply(dl_url, contenido)
contenidos[sapply(contenidos, is.null)] <- "NULL"
contenidos2 <- contenidos %>% unlist() %>% c()

content <- c()
for (url in dl_url[1:5]){
        cont <- contenido(url)
        content <- c(content, cont)
}

titulos <- sapply(dl_url, titulo)
titulos2 <- unlist(titulos) %>% c()
fechas <- sapply(dl_url, fecha)
fechas2 <- unlist(fechas) %>% c()

titulos[sapply(titulos, is.null)]

noticias <- data.frame(contenidos2, fechas, titulo, stringsAsFactors = F)

write.csv(noticias, "./noticias csv/diario_libre_noticias.csv")




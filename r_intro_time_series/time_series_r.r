
# Librerías
suppressPackageStartupMessages(library(stringr))    # manejo de strings (caracteres)
suppressPackageStartupMessages(library(zoo))        # manejo de clases para series temporales
suppressPackageStartupMessages(library(lubridate))  # manejo de fechas
suppressPackageStartupMessages(library(xts))        # manejo de clases para series temporales, incluye series irreg
suppressPackageStartupMessages(library(quantmod))   # manejo del workflow de modelos cuantitativos financieros
suppressPackageStartupMessages(library(tseries))    # manejo de series irregulares
suppressPackageStartupMessages(library(forecast))   # varios metodos para pronóstico
suppressPackageStartupMessages(library(TSstudio))   # gráficos y análisis de series de tiempo usando plotly
suppressPackageStartupMessages(library(plyr))       # métodos para split-apply-combine usando dataframes  
suppressPackageStartupMessages(library(dplyr))      # manipulacion de datos - tidyverse
suppressPackageStartupMessages(library(tidyr))      # manipulación de datos - tidyverse (spread, gather)
suppressPackageStartupMessages(library(Hmisc))      # algunas funciones de interes para describir datos 
suppressPackageStartupMessages(library(data.table)) # manipulacion de datos mayor rapidez que dplyr
suppressPackageStartupMessages(library(readxl))     # lectura de archivos de excel
suppressPackageStartupMessages(library(IRdisplay))  # despliegue de resultados en jupyter para R
suppressPackageStartupMessages(library(xtable))     # manejo de formato de tablas en R
suppressPackageStartupMessages(library(ggplot2))    # manipulacion de graficos - tidyverse
suppressPackageStartupMessages(library(scales))     # manejo de escalas en ggplot2
suppressPackageStartupMessages(library(corrplot))   # grafico de correlacion

# Datos ####
data.dir <- "./data/Rossmann\ Store\ Sales"

# data.table más rápido en la extracción y manipulación
train <- fread(paste0(data.dir, "/train.csv"), stringsAsFactors = T)
test  <- fread(paste0(data.dir, "/test.csv"), stringsAsFactors = T)
store <- fread(paste0(data.dir, "/store.csv"), stringsAsFactors = T)

# Train data set
train.store <- merge(train, store, by = "Store")

train.store[ , Date := as.Date(Date)]
train.store <- train.store[order(Store, Date)]

# Test data set
test.store <- merge(test, store, by = "Store")

test.store[ , Date := as.Date(Date)]
test.store <- test.store[order(Store, Date)]

print("Fin")

# Sumario Train
dim(train.store)
str(train.store)
summary(train.store)
describe(train.store)
head(train.store)

# Sumario Test
dim(test.store)
str(test.store)
summary(test.store)
describe(test.store)
head(test.store)

# Comparativo de variables: train vs test 
names(test.store)
setdiff(names(train.store), names(test.store))
setdiff(names(test.store), names(train.store))

# Ventas Totales
train.all.sum <- as.data.frame(train.store) %>%
  group_by(Date) %>% 
  summarise(Sales = sum(as.numeric(Sales), na.rm = TRUE)) %>% 
  ungroup()

head(train.all.sum)

# Gráfico de Ventas Totales ####
Date <- train.all.sum$Date

# xts
xts.all.sales <- xts(train.all.sum$Sales, order.by = Date)

# TSstudio
ts_plot(xts.all.sales, 
        title = "Rossmann Stores - Ventas Totales",
        Xtitle = "Fuente: Rossmann Store Sales (Kaggle)", 
        Ytitle = "Sales",
        slider = TRUE
        )

# Gráfico de Ventas Totales: Fines de Semana vs Días de Semana

train.dweek.sum <- as.data.frame(train.store) %>%
  mutate(wkend_sales = ifelse(DayOfWeek %in% c(6,7), Sales, 0), 
         wkday_sales = ifelse(!DayOfWeek %in% c(6,7), Sales, 0)) %>%
  group_by(Date) %>% 
  summarise(wkend_sales = sum(wkend_sales, na.rm = T), 
            wkday_sales = sum(wkday_sales, na.rm = T)) %>% 
  ungroup()

xts.dweek.sales <- xts(cbind(train.dweek.sum$wkend_sales, 
                             train.dweek.sum$wkday_sales), 
                       order.by = Date)

#index.wkday <- which(   .indexwday(xts.all.sales) != 6 
#                      & .indexwday(xts.all.sales) != 0)

#index.wkend <- which(   .indexwday(xts.all.sales) == 6 
#                      | .indexwday(xts.all.sales) == 0)

ts_plot(xts.dweek.sales, 
        title = "Rossmann Stores - Ventas Totales (Fines de Semana vs Resto)",
        Xtitle = "Fuente: Rossmann Store Sales (Kaggle)", 
        Ytitle = "Sales",
        type = "single",
        slider = TRUE
        )

# Gráfico de Ventas Totales: Domingos y Feriados

#holidays <- as.data.frame(train.store) %>%
#   dplyr::select(Date, StateHoliday) %>%
#   filter(as.character(StateHoliday) != '0') %>%
#   dplyr::select(Date) %>%
#   distinct()

# str(holidays)

# holidays.dt <- as.Date(holidays[[1]])

# str(holidays.dt)

# Aunque la variable StateHoliday marca los días festivos, parece que no excluye los festivos laborables
# Por eso usamos el siguiente listado:
holidays <- c(
              "2013-01-01", "2013-01-06", "2013-03-29", "2013-04-01", 
              "2013-05-01", "2013-05-09", "2013-05-12", "2013-05-20", 
              "2013-10-03", "2013-12-25", "2013-12-26", "2014-01-01", 
              "2014-04-18", "2014-04-21", "2014-05-01", "2014-05-11", 
              "2014-05-29", "2014-06-09", "2014-10-03", "2014-12-25", 
              "2014-12-26", "2015-01-01", "2015-04-03", "2015-04-06", 
              "2015-05-01", "2015-05-10", "2015-05-14", "2015-05-25"
              )

holidays.dt <- sapply(holidays, function(x) {as.Date(x)})

index.holiday <- which( .indexwday(xts.all.sales) == 0 
                      | index(xts.all.sales) %in% holidays.dt)

ts_plot(xts.all.sales[index.holiday], 
        title = "Rossmann Stores - Ventas Totales (Domingos y Feriados)",
        Xtitle = "Fuente: Rossmann Store Sales (Kaggle)", 
        Ytitle = "Sales",
        slider = TRUE
       )

# Gráfico de Ventas Totales: Excluyendo Domingos y Feriados

index.noholiday <- which( .indexwday(xts.all.sales) != 0 
                       & !(index(xts.all.sales) %in% holidays.dt))

ts_plot(xts.all.sales[index.noholiday], 
        title = "Rossmann Stores - Ventas Totales (Sin Domingos ni Feriados)",
        Xtitle = "Fuente: Rossmann Store Sales (Kaggle)", 
        Ytitle = "Sales",
        slider = TRUE
        )

train.store.null <- train.store %>%
  dplyr::select(Store, Sales, Open) %>%
  filter(Open == 0 | Sales == 0) %>%
  mutate(store_close = as.numeric(Open == 0)) %>%
  mutate(store_nsale = as.numeric(Open == 1 & Sales == 0)) %>%
  summarise(closed_store_events = sum(store_close),
            null_sales_events = sum(store_nsale),
            store_nd = n_distinct(Store)
           )

train.store.null

print(paste("% de registros (tienda, día) con tienda cerrada y/o cero ventas:", 
            (train.store.null$closed_store_events 
             + train.store.null$null_sales_events) 
            / nrow(train.store) * 100)
     )

train.store %>% 
 summarise_all(funs(sum(is.na(.)))) %>%
 select_if(. > 0)

store %>% 
 summarise_all(funs(sum(is.na(.)))) %>%
 select_if(. > 0)

### Versión de train.store con tratamiento de valores perdidos
train.store.clean <- train.store %>%
  filter(Open != 0 & Sales != 0) %>%
  mutate(CompetitionDistance = ifelse(is.na(CompetitionDistance)==TRUE, 
                                      median(CompetitionDistance, na.rm = T),
                                     CompetitionDistance)) %>%
  mutate(CompetitionOpenSinceMonth = ifelse(is.na(CompetitionOpenSinceMonth)==TRUE, 0,
                                     CompetitionOpenSinceMonth)) %>%
  mutate(CompetitionOpenSinceYear = ifelse(is.na(CompetitionOpenSinceYear)==TRUE, 0,
                                     CompetitionOpenSinceYear)) %>%
  mutate(Promo2SinceWeek = ifelse(is.na(Promo2SinceWeek)==TRUE, 0,
                                    Promo2SinceWeek)) %>%
  mutate(Promo2SinceYear = ifelse(is.na(Promo2SinceYear)==TRUE, 0,
                                     Promo2SinceYear))
  
  
train.store.clean %>% 
 summarise_all(funs(sum(is.na(.)))) %>%
 dplyr::select(CompetitionDistance, CompetitionOpenSinceMonth, CompetitionOpenSinceYear, 
               Promo2SinceWeek, Promo2SinceYear)

train.store.new <- train.store.clean %>%
  mutate(Year = year(Date),
         Month = month(Date),
         Day = day(Date),
         WeekOfYear = week(Date)) %>%
  mutate(SalesPerCustomer = Sales / Customers) %>%
  mutate(SchoolHoliday = as.numeric(as.character(SchoolHoliday))) %>%
  # Dias abiertos a la competencia y a promociones:
  mutate(CompetitionOpen = 12 * (Year - CompetitionOpenSinceYear) + (Month - CompetitionOpenSinceMonth), 
         PromoOpen = 12 * (Year - Promo2SinceYear) + (WeekOfYear - Promo2SinceWeek) / 4.0)


train.store.type.mean <- train.store.new %>%
  dplyr::select(StoreType, Sales, Customers, SalesPerCustomer, CompetitionDistance, CompetitionOpen, PromoOpen) %>%
  # mutate(store_id  = paste0("s-", str_pad(as.character(Store), 4, "left", pad = "0"))) %>%
  group_by(StoreType) %>%
  summarise_all(funs(mean(.)))
  # unite(type_assort, StoreType, Assortment, sep = "_") %>%
  # spread(type_assort, avg_sales, fill = 0)

train.store.type.sum <- train.store.new %>%
  dplyr::select(StoreType, Sales, Customers) %>%
  group_by(StoreType) %>%
  summarise_all(funs(sum(as.numeric(.))))

xtable(train.store.type.sum, auto = TRUE)
xtable(train.store.type.mean, auto = TRUE)

# By week
train.store.type.week <- train.store.new %>%
  dplyr::select(StoreType, Store, Year, WeekOfYear, Sales) %>%
  group_by(StoreType, Store, Year, WeekOfYear) %>%
  summarise_all(funs(sum(.)))

head(train.store.type.week)

# Empirical Cumulative Distribution Function (ECDF) por Tienda en cada Tipo de Tienda

# Función para generar ECDF de cada tienda y asociar su tipo 
ts_ecdf <- function(store){
    Store <- unique(store$Store)
    StoreType <- unique(store$StoreType)
    Fn <- ecdf(store$Sales)
  
    y.list <- list()
    y.list <- list(StoreType = StoreType, Store = Store, Fn = Fn)
    
    return(y.list)
}

# Función para colocar en un mismo gráfico las ECDFs de las tiendas de un mismo tipo como argumento
plot_ts_ecdf <- function(type, xmax = 240000){
    ecdf.ls <- dlply(train.store.type.week %>% filter(StoreType == type), .(Store), ts_ecdf)
    # str(ecdf.a.ls)
    # str(sapply(ecdf.a.ls, function(x) x[3]))
    ll <- Map(f  = stat_function, 
          colour = rainbow(length(sapply(ecdf.ls, function(x) x[3]))),
          fun = sapply(ecdf.ls, function(x) x[3]), geom = 'step')
    g <- ggplot(data = data.frame(x = c(0, xmax)), aes(x = x)) + ll + labs(title=paste("ECDFs StoreType =", type), x ="Sales")
    
    return(g)
                       }

plot_ts_ecdf("a")

plot_ts_ecdf("b")

plot_ts_ecdf("c")

plot_ts_ecdf("d")

# Por tipo de surtido
train.store.assort.mean <- train.store.new %>%
  dplyr::select(Assortment, Sales, Customers, SalesPerCustomer, 
                CompetitionDistance, CompetitionOpen, PromoOpen) %>%
  group_by(Assortment) %>%
  summarise_all(funs(mean(.)))

train.store.assort.sum <- train.store.new %>%
  dplyr::select(Assortment, Sales, Customers) %>%
  group_by(Assortment) %>%
  summarise_all(funs(sum(as.numeric(.))))

xtable(train.store.assort.sum, auto = TRUE)
xtable(train.store.assort.mean, auto = TRUE)

train.store.promo.dweek <- train.store.new %>%
  dplyr::select(Promo, Promo2, DayOfWeek, Sales) %>%
  mutate(group = as.factor(paste("Promo =", as.character(Promo), "|", "Promo2 =", as.character(Promo2)))) %>%
  group_by(DayOfWeek, group) %>%
  summarise(avg_sales = mean(Sales))

ggplot(train.store.promo.dweek, aes(group)) + 
geom_line(aes(x = DayOfWeek, y = avg_sales)) +
facet_wrap(~ group)

train.store.corr <- train.store.new %>%
  dplyr::select(-Open) %>%
  select_if(is.numeric)

train.corr.mat <- cor(train.store.corr)

corrplot(train.corr.mat, method = "color", type = "upper")

# Función para generar gráficos de estacionalidad por tienda, remuestreando a frecuencia semanal
# Hace sentido reducir la frecuencia de días a semanas para presentar los patrones de estacionalidad más claramente

ts_season <- function(store){
    y <- as.data.frame(train.store.new) %>%
         filter(Store == store) %>%
         group_by(Store, StoreType, Date) %>% 
         summarise(Sales = sum(as.numeric(Sales))) %>% 
         ungroup()
    
    Date <- y$Date
    
    y.xts.w <- apply.weekly(xts(y$Sales, order.by = Date), drop.time = FALSE, sum)
    
    tsplot <- ts_plot(y.xts.w,
        title = paste("Rossmann Stores - Ventas Semanales de la Tienda", y$Store, "Tipo =", y$StoreType),
        Ytitle = "Sales",
        type = "single"
       )
    
    return(tsplot)
}

ts_season(2)  # a
ts_season(85) # b
ts_season(1)  # c
ts_season(13) # d

# Función para generar gráficos de tendencia por tienda

ts_trend <- function(store){
    y <- as.data.frame(train.store.new) %>%
         filter(Store == store) %>%
         group_by(Store, StoreType, Date) %>% 
         summarise(Sales = sum(as.numeric(Sales))) %>% 
         ungroup()
    
    Date <- y$Date
    
    y.xts <- xts(y$Sales, order.by = Date)
    
    attr(y.xts, 'frequency') <- 365

    y.xts.decomp <- decompose(as.ts(y.xts), type = "additive")

    tsplot <- ts_plot(xts(y.xts.decomp$trend, order.by = Date),
        title = paste("Rossmann Stores - Tendencia Ventas de la Tienda", y$Store, "Tipo =", y$StoreType),
        Ytitle = "Sales",
        type = "single"
       )
    
    return(tsplot)
}

ts_trend(2)  # a
ts_trend(85) # b
ts_trend(1)  # c
ts_trend(13) # d

# Función para generar gráficos de autocorrelación (ACF, PACF) por tienda

ts_autocorr <- function(store, lag = 50){
    y <- as.data.frame(train.store.new) %>%
         filter(Store == store) %>%
         group_by(Store, StoreType, Date) %>% 
         summarise(Sales = sum(as.numeric(Sales))) %>% 
         ungroup()
    
    Date <- y$Date
    
    y.xts <- na.omit(xts(y$Sales, order.by = Date))
    
    yacf  <- acf(y.xts, lag.max = lag)
    ypacf <- pacf(y.xts, lag.max = lag)
     
    return(list(yacf, ypacf))
}

# Tienda 2  (Tipo "a")
ts_autocorr(2)

# Tienda 85 (Tipo "b")
ts_autocorr(85)

# Tienda 1 (Tipo "c")
ts_autocorr(1)

# Tienda 3 (Tipo "d")
ts_autocorr(13)

# Funcion para generar los modelos ARIMA por tienda

ts_arima <- function(store){
    Date <- store$Date
    y.xts <- xts(store$Sales, order.by = Date)
    y.fit <- auto.arima(y.xts, lambda = BoxCox.lambda(y.xts))
    return(y.fit)
}

system.time(
    out.arima <- dlply(train.store.new, .(Store), ts_arima)
)

str(out.arima)

str(train.store.new)

## variables with single value
which(sapply(train.store.new, function(x) { length(unique(x)) }) == 1)
## count levels before dropping redundant ones
sapply(train.store.new[sapply(train.store.new, is.factor)], nlevels)
## extract factor columns and drop redundant levels
fctr <- lapply(train.store.new[sapply(train.store.new, is.factor)], droplevels)
## count levels after dropping redundant ones
sapply(fctr, nlevels)

# Funcion para generar los modelos TSLM por tienda

tslm_fit = function(store){
  Sales <- ts(store$Sales, frequency = 365)
  DayOfWeek <- store$DayOfWeek
  StateHoliday <- droplevels(store$StateHoliday)
  SchoolHoliday <- store$SchoolHoliday
  Promo <- store$Promo
  Promo2 <- store$Promo2
  if(nlevels(StateHoliday)>1) {
  fit <- tslm(Sales ~ trend + season + 
                      DayOfWeek + StateHoliday + SchoolHoliday + 
                      Promo + Promo2
             )
  } else {
  fit <- tslm(Sales ~ trend + season + 
                      DayOfWeek + SchoolHoliday + 
                      Promo + Promo2
             )   
  }
  return(fit)
}

system.time(
    out.tslm <- dlply(train.store.new, .(Store), tslm_fit)
)

str(out.tslm)

min(test.store$Date)
max(test.store$Date)

max(test.store$Date) - min(test.store$Date)
as.numeric(max(test.store$Date) - min(test.store$Date)) / 7

fcast.arima <- lapply(out.arima, function(x) forecast(x, h=47))

str(fcast.arima)

# Ejemplo pronóstico con tienda 2
plot(fcast.arima[[2]])

# Funcion para pronosticar con nuevos datos en base a los modelos TSLM por tienda

tslm_forecast = function(x, y){
  index <- x$Store[1]
  fitt <- y[[index]]
  #if(nlevels(x$StateHoliday)>1) {
  return(data.frame(forecast(fitt, newdata = data.frame(DayOfWeek = x$DayOfWeek, 
                                                        StateHoliday = x$StateHoliday, 
                                                        SchoolHoliday = x$SchoolHoliday,
                                                        Promo = x$Promo,
                                                        Promo2 = x$Promo2)
                            )
                   )
        )
  #} else {
  #return(data.frame(forecast(fitt, newdata = data.frame(DayOfWeek = x$DayOfWeek, 
  #                                                      SchoolHoliday = x$SchoolHoliday,
  #                                                      Promo = x$Promo,
  #                                                      Promo2 = x$Promo2)
  #                          )
  #                 )
  #      )  
  #}
}

system.time(
    predictions <- ddply(test, .(Store), tslm_forecast, out.tslm)
)

str(predictions)

predictions$Point.Forecast <- ifelse(predictions$Point.Forecast < 0, 0, 
                                     predictions$Point.Forecast)

Avg_Sales <- train[,.(AS = mean(Sales,na.rm=T)),.(Store,DayOfWeek)]
test <- merge(test,Avg_Sales, by = c("Store","DayOfWeek"))
test <- test[order(Store,Date)]
test[,FPPredictions:=Open * predictions$Point.Forecast]
test[,FPredictions:=ifelse(is.na(predictions$Point.Forecast),AS,predictions$Point.Forecast)]

results <- data.frame(Id=test$Id, Sales=test$FPredictions)
results <- results[order(results$Id),]

# Tasa de Cambio Diaria DOP/USD Entidades Financieras BCRD

# Web download ####
url <- "https://www.bancentral.gov.do/tasas_cambio/TASA_ENTIDADES_FINANCIERAS.xls?s=1525718479909"
destfile <- "TASA_ENTIDADES_FINANCIERAS.xls"
curl::curl_download(url, destfile)

# Archivos crudos ####
raw.diaria <- read_excel(destfile, sheet = "Diaria", 
                  col_names = TRUE, skip = 1) %>% 
  select_all(tolower)

# Limpieza y Transformaciones ####

# cat(unique(raw.diaria$mes), sep = '", "')

mes <- data.frame(
       mes = c("Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", 
               "Ago", "Sep", "Sept", "Oct", "Nov", "Dic"),
       mm = c("01", "02", "03", "04", "05", "06", "07", "08", 
              "09", "09", "10", "11", "12"),
       stringsAsFactors = FALSE
         )

etl.diaria <- raw.diaria %>%
  left_join(mes, by = "mes") %>% 
  mutate(tdate = as.Date(paste0(año, "-", mm, "-", día))) %>% 
  mutate(diff = venta - compra,
         spread = 100 * (diff / venta)) %>% 
  filter(is.na(tdate)==FALSE)

dates <- etl.diaria$tdate

xts.compra <- xts(etl.diaria$compra, order.by = dates)
xts.venta <- xts(etl.diaria$venta, order.by = dates)
xts.diff <- xts(etl.diaria$diff, order.by = dates)
xts.spread <- xts(etl.diaria$spread, order.by = dates)

print("Fin")

xts.all <- cbind(xts.venta, xts.compra, xts.diff, xts.spread)
names(xts.all) <- c("Venta", "Compra", "Diferencia", "Spread")

ts_plot(xts.venta, 
        title = "Tasa de Venta (DOP$ / USD$)",
        Xtitle = "Fuente: Banco Central de la República Dominicana", 
        Ytitle = "",
        slider = TRUE,
        col = "blue"
       )

ts_plot(xts.spread, 
        title = "Spread (DOP$ / USD$)",
        Xtitle = "Fuente: Cálculo a partir de datos del Banco Central de la República Dominicana", 
        Ytitle = "%",
        slider = TRUE,
        type = "single",
        col = "red"
       )

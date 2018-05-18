Para trabajar sobre el notebook time_series_r.ipynb es preciso instalar:

[Anaconda](https://www.anaconda.com/download/) 

Si no quieren que el R de Anaconda interfiere que el R de su maquina local, crear un environment:

```conda
conda info --envs
conda remove --name condaR --all
conda info --envs
conda create --name condaR
```
```conda
source activate condaR
```
Luego configurar e instalar:

```conda
conda config --add channels defaults
conda config --add channels r
conda config --add channels conda-forge
conda update --all
conda install -c conda-forge jupyter
conda install -c r r-essentials
conda install -c r r-devtools
conda install -c r r-irdisplay
```

En el R de Anaconda:
IRkernel::installspec()  # para registrar el kernel en la instalación de R

Paquetes de R a instalar en distribucion Anaconda. Nota: Anaconda les coloca un prefijo "r-" a los paquetes de su distribucion
Si no encuentran dicho paquete en Anaconda instalar normal en el ambiente R de Anaconda usando CRAN (https://cran.r-project.org/web/packages/index.html)

```conda
conda install -c r r-stringr
conda install -c r r-zoo
conda install -c r r-lubridate
conda install -c r r-xts
conda install -c r r-quantmod
conda install -c r r-tseries
conda install -c r r-forecast
conda install -c r r-TSstudio
conda install -c r r-plyr 
conda install -c r r-dplyr
conda install -c r r-tidyr
conda install -c r r-Hmisc
conda install -c r r-data.table
conda install -c r r-readxl
conda install -c r r-xtable
conda install -c r r-ggplot2
conda install -c r r-scales
conda install -c r r-corrplot
```
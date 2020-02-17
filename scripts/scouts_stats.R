require("tidyverse")

input_dir <- 'data/sample data/cytof gio'
input_file <- 'raw_data.xlsx'
file_path <- stringr::str_c(input_dir, '/', input_file)

data <- readxl::read_excel(file_path)
data %>% 
  dplyr::select(-1) %>%  # drop first column (samples)
  mvoutlier::pcout(makeplot = TRUE)  # multivariate outlier analysis

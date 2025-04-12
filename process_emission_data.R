library(tidyverse)
library(readr)
library(stringr)

dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)
csv_files <- list.files(path = "data", pattern = "data_.*\\.csv$", full.names = TRUE)

process_file <- function(file_path) {
  region <- str_extract(basename(file_path), "(?<=data_).*(?=\\.csv)")
  
  df <- read_csv(file_path)
  emission_type_col <- names(df)[1]
  
  df_long <- df %>%
    pivot_longer(
      cols = -1,
      names_to = "Year",
      values_to = "Value"
    ) %>%
    rename(
      "Emission Type" = 1  # Rename the first column
    ) %>%
    mutate(
      Region = region,
      Year = as.integer(Year)
    ) %>%
    select(`Emission Type`, Region, Year, Value)
  
  return(df_long)
}

full_data <- map_df(csv_files, process_file) %>%
  write_csv("data/processed/full_data.csv")



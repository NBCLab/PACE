library("nlme")
library("stargazer")
require(table1)
library(broom)
library(broom.mixed)
library("lmerTest")


dsets <- c("ALC", "ATS", "CANN", "COC")
gsrs <- c("-gsr", "")
combats <- c("-combat", "")
metrics <- c("REHO", "FALFF")
seeds <- c("amygdala", "hippocampus", "insula", "striatum", "vmPFC")

for (dset in dsets){
  der_dir <- c("/gpfs1/home/m/r/mriedel/pace/dsets/dset-", dset,"/derivatives/")
  cov_path <- paste0(der_dir, dset,"-sumstats_table.txt")
  cova <- read.table(file=cov_path, sep = '\t', header = TRUE)
  for (gsr in gsrs){
    if ( gsr=="" ) {
      gsr_t <- "GSR=False"
    } else {
      gsr_t <- "GSR=True"
    }
    for (combat in combats){
      for (metric in metrics){
        dat_path <- paste0(der_dir, dset, "-", metric, gsr, combat, ".tsv")
        dat_orig <- read.table(file=dat_path, sep = '\t', header = TRUE)
        dat <- merge(x = dat_orig, y = cova[, c("participant_id", "site", "group", "gender", "age")], by = "participant_id", all = TRUE)
        
        dat[dat==""] <- NA
        dat <- na.omit(dat)
        
        rois <- colnames(dat_orig)[2:length(colnames(dat_orig))]
        for (seed in seeds){
          if (seed == "vmPFC") {
            hemispheres <- c("")
            } else {
            hemispheres <- c("lh", "rh")
          }
          
          if (seed != "striatum") {
            lm.linear <- vector("list", 6)
            lm.mlm <- vector("list", 6)
            lm.combat <- vector("list", 6)
            i <- 1
          }
          for (hemis in hemispheres) {
            if (seed == "amygdala") {
              rois <- c(paste0("amygdala1", hemis), paste0("amygdala2", hemis), paste0("amygdala3", hemis))
              } else if (seed == "hippocampus") {
                rois <- c(paste0("hippocampus3solF1", hemis), paste0("hippocampus3solF2", hemis), paste0("hippocampus3solF3", hemis))
              } else if (seed == "insula") {
                rois <- c(paste0("insulaD", hemis), paste0("insulaP", hemis), paste0("insulaV", hemis))
              } else if (seed == "striatum") {
                rois <- c(paste0("striatumMatchCD", hemis), paste0("striatumMatchCV", hemis), paste0("striatumMatchDL", hemis), paste0("striatumMatchD", hemis), paste0("striatumMatchR", hemis), paste0("striatumMatchV", hemis))
                lm.linear <- vector("list", 6)
                lm.mlm <- vector("list", 6)
                lm.combat <- vector("list", 6)
                i <- 1
              } else if (seed == "vmPFC") {
                rois <- c("vmPFC1", "vmPFC2", "vmPFC3", "vmPFC4", "vmPFC5", "vmPFC6")
            }
            
            for (roi in rois) {
              message(paste('Processing dataset', dset, gsr, combat, metric, roi))
              if ( combat=="" ) {
                # Regression Fit: 3dttest++
                equation_linear <- sprintf('%s ~ group + site + gender + age', roi)
                print(equation_linear)
                lm.linear[[i]] <- lm(equation_linear, dat)
                write.csv(tidy(lm.linear[[i]]) , paste0("/Users/jperaza/Desktop/pace/metrics/indiv_tables/", dset, "-", metric, "-", roi, gsr, combat, "-lm", ".csv"))
                
                # Multilevel Modeling
                equation_lml <- sprintf('%s ~ group + gender + age + (1|site)', roi)
                message(equation_lml)
                lm.mlm[[i]] <- lmer(formula(equation_lml), data = dat)
                write.csv(tidy(lm.mlm[[i]], effects="fixed"), paste0("/Users/jperaza/Desktop/pace/metrics/indiv_tables/", dset, "-", metric, "-", roi, gsr, combat, "-mlm", ".csv"))
                class(lm.mlm[[i]]) <- "lmerMod" # Modify the class so that it works with stargazer
              } else {
                # Regression Fit: combat
                equation_combat <- sprintf('%s ~ group + gender + age', roi)
                message(equation_combat)
                lm.combat[[i]] <- lm(equation_combat, dat)
                write.csv(tidy(lm.combat[[i]]), paste0("/Users/jperaza/Desktop/pace/metrics/indiv_tables/", dset, "-", metric, "-", roi, gsr, combat, ".csv"))

              }
              
              i <- i + 1
            } 
            
            if ( seed=="striatum" ) {
              if ( combat=="" ) {
                title_linear <- paste('Results:', dset, gsr_t, "ComBat=False. LM.", metric, seed, hemis)
                out_linear <- paste0(der_dir, "tables/", dset, "-1", gsr, combat, "-", metric, "-", seed, hemis, ".tex")
                stargazer(lm.linear, title=title_linear, align=TRUE, type="latex", out=out_linear, float=TRUE, header=FALSE)
                
                title_mlm <- paste('Results:', dset, gsr_t, "ComBat=False. LME.", metric, seed, hemis)
                out_mlm <- paste0(der_dir, "tables/", dset, "-2", gsr, combat, "-", metric, "-", seed, hemis, ".tex")
                stargazer(lm.mlm, title=title_mlm, align=TRUE, type="latex", out=out_mlm, float=TRUE, header=FALSE)
              } else {
                title_combat <- paste('Results:', dset, gsr_t, "ComBat=True. LM.", metric, seed, hemis)
                out_combat <- paste0(der_dir, "tables/", dset, "-3", gsr, combat, "-", metric, "-", seed, hemis, ".tex")
                stargazer(lm.combat, title=title_combat, align=TRUE, type="latex", out=out_combat, float=TRUE, header=FALSE)
              }
              
            }
            
          }
          if ( seed!="striatum" ) {
            if ( combat=="" ) {
              title_linear <- paste('Results:', dset, gsr_t, "ComBat=False. LM.", metric, seed)
              out_linear <- paste0(der_dir, "tables/", dset, "-1", gsr, combat, "-", metric, "-", seed, ".tex")
              stargazer(lm.linear, title=title_linear, align=TRUE, type="latex", out=out_linear, float=TRUE, header=FALSE)
            
              title_mlm <- paste('Results:', dset, gsr_t, "ComBat=False. LME.", metric, seed)
              out_mlm <- paste0(der_dir, "tables/", dset, "-2", gsr, combat, "-", metric, "-", seed, ".tex")
              stargazer(lm.mlm, title=title_mlm, align=TRUE, type="latex", out=out_mlm, float=TRUE, header=FALSE)
            } else {
              title_combat <- paste('Results:', dset, gsr_t, "ComBat=True. LM.", metric, seed)
              out_combat <- paste0(der_dir, "tables/", dset, "-3", gsr, combat, "-", metric, "-", seed, ".tex")
              stargazer(lm.combat, title=title_combat, align=TRUE, type="latex", out=out_combat, float=TRUE, header=FALSE)
            }
          }
        }
      }
    }
  }
}
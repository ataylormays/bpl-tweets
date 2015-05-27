library(data.table)

season_split <- function(x){
  
    s <- unlist(strsplit(x, ", "))
    
    f <- function(s){
      s <- unlist(strsplit(s, " - "))
      if(length(s) == 1){
        s = c(s, "2015")
      }
      start <- as.numeric(s[1])
      end <- as.numeric(s[2])
      nxt <- start + 1
      seasons <- c()
      while(nxt <= end){
        seasons <- c(seasons, paste(start, nxt, sep="-"))
        start=nxt
        nxt=nxt+1
      }
      return(seasons)
  }
  
  results <- unname(unlist(sapply(s, function(x) f(x))))
  return(paste(results, collapse=", "))
  
}

find_start <- function(s){
  s <- unlist(strsplit(s, ", "))
  max <- 0
  for(i in length(s)){
    if(as.numeric(substring(s[i], 1, 4)) > max){
      max <- as.numeric(substring(s[i], 1, 4))
    }
  }
  return(max)

}

clubs <- fread("C:/Users/ataylor/Documents/Projects/web apps/epl twitter/data/epl_clubs.csv")

setnames(clubs, c("club", "town", "tot_seasons", "tot_spells", "longest_spell", 
                  "last_promo", "last_rlgn", "tot_abs", "seasons", "most_rec_finish", 
                  "highest_finish", "top_scorer"))

clubs[,seasons:=sapply(seasons, function(x) season_split(x))]
clubs[,start:=sapply(seasons, function(x) find_start(x))]

twitter_clubs <- clubs[start >= 2007]

twitter_clubs_dt <- data.table(club = twitter_clubs$club, hashtags = rep('', length(twitter_clubs$club)))

write.csv(twitter_clubs_dt, "C:/Users/ataylor/Documents/Projects/web apps/epl twitter/data/twitter_clubs.csv", row.names=FALSE)

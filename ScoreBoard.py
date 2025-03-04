from selenium import webdriver 
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.by import By
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import re
import sys

class Batsman:
    def __init__(self,Name:str=''):
        self.Name:str=Name
        self.runs_made:int=0
        self.balls_faced:int=0
        self.fours:int=0
        self.sixes:int=0
        self.strike_rate:float=0.0
        self.status:str='not out'
        
class Bowler:
    def __init__(self,Name:str=''):
        self.Name:str=Name
        self.overs:float=0
        self.maidens:int=0
        self.runs_given:int=0
        self.wickets:int=0
        self.economy:float=0.0   

def main() -> None:
    urls=[]
    # with open('matches.txt','r') as file:
    #     for line in file.readlines():
    #         urls.append(line)
    # get_commentary(urls)       
    for i in range(1,26): 
        file1=open(f'match\\match{i}Innings1.txt','r')
        team1=file1.read().split('\n')
        file1.close()
        team1=team1[::-1]

        file2=open(f'match\\match{i}Innings2.txt','r')
        team2=file2.read().split('\n')
        file2.close()
        team2=team2[::-1]      

        print_score_board(team1,i)
        print_score_board(team2,i)
    
def print_score_board(team:list[str],count) -> None:
    Batsmans,Bowlers,Team_score,Wickets,Extras,Overs,over=find_score(team)
    
    if Team_score==0 and Overs==0:
        print('Check Internet Connection and try again',count)   
    with open(f'score\\match{count}.txt','a') as file:
        file.write(f'{Team_score} {Wickets} {Extras} {Overs}.{over}'+'\n\n')
        for players in Batsmans:
            if players.balls_faced == 0 : players.strike_rate = 0
            else : players.strike_rate=round((players.runs_made/players.balls_faced)*100)
            file.write(f'{players.Name} {players.runs_made} {players.balls_faced} {players.fours} {players.sixes} {players.strike_rate}'+'\n')
            file.write(f'{players.status}'+'\n\n')
        file.write('\n')        
        
        for players in Bowlers:
            try:
                players.overs=round(players.overs,1)
                x=(players.overs-int(players.overs))*10/6
                players.economy=round(players.runs_given/(int(players.overs)+x),2)
                file.write(f'{players.Name} {players.overs} {players.maidens} {players.runs_given} {players.wickets} {players.economy}'+'\n')
            except :
                players.economy=0   
                file.write(f'{players.Name} {players.overs} {players.maidens} {players.runs_given} {players.wickets} {players.economy}'+'\n') 
        file.write('\n')    

def get_commentary(urls:list[str]) -> None:
    
    chrome_service=Service(ChromeDriverManager().install())
    browser=webdriver.Chrome(service=chrome_service)
    browser.maximize_window()
    count=1
    for url in urls:
        try:
            url=url.replace('live-cricket-scores','cricket-full-commentary')
            browser.get(url)
            teams=browser.find_elements(By.CSS_SELECTOR,'.ng-binding.cb-nav-pill-1')
                
            teams[1].click()     
            sleep(5)
            para=browser.find_elements(By.CSS_SELECTOR,'p')
            paras=[]
            for i in para:
                paras.append(i.text+'\n')
            with open(f'match\\match{count}Innings1.txt','w') as file:
                file.writelines(paras)
                
            teams[2].click()    
            sleep(5)
            para=browser.find_elements(By.CSS_SELECTOR,'p')
            paras=[]
            for i in para:
                paras.append(i.text+'\n')
            with open(f'match\\match{count}Innings2.txt','w') as file:
                file.writelines(paras)  
            print(count)
            sleep(3)    
            count+=1    
        except StaleElementReferenceException:
            print('Check Internet Connection and try again',count)   
        except:
            print('Invalid Url',count)     
    browser.close()
        
        

def temp(Bat:Batsman,Ball:Bowler,scores:list[str],score:list[str],Team_Score:int,maiden:int,i:int=0,extra:int=0) -> tuple[int,int]:
    if score[i]=='4 runs':
        score[i]='FOUR'
    elif score[i]=='6 runs':
        score[i]='SIX'    
    Bat.balls_faced+=1
    runs=scores.index(score[i])
    if runs == 0 : maiden+=1
    Bat.runs_made+=runs
    if runs==4 : Bat.fours+=1
    elif runs==6 : Bat.sixes+=1 
    Ball.runs_given+=runs+extra
    return Team_Score+runs+extra,maiden

def find_batman_index(Batsmans:list[Batsman],Batman:str) -> Batsman:
    for i in range(len(Batsmans)):
        if(Batsmans[i].Name==Batman):
            return Batsmans[i]
    Batsmans.append(Batsman(Batman))  
    return Batsmans[-1]            
        
def find_bowler_index(Bowlers:list[Bowler],bowler:str) -> Bowler:
    for i in range(len(Bowlers)):
        if(Bowlers[i].Name==bowler):
            return Bowlers[i]
    Bowlers.append(Bowler(bowler))
    return Bowlers[-1]

def find_score(commentary:list[str]) -> tuple[list[Batsman],list[Bowler],int,int,int,int,int]:
    Bowlers=[]
    Batsmans=[]
    Team_Score=Wickets=Extras=over=maiden=Overs=0
    Bat,Ball=Batsman(),Bowler()
    scores=['no run','1 run','2 runs','3 runs','FOUR','5 runs','SIX']
    others=['leg byes','byes','no ball','wide','2 wides','3 wides','4 wides','5 wides']
    pattern=r'(.+) to ([a-zA-Z- ]+), ((?:(?:(?:byes|leg byes|no ball), )?(?:[23456] runs|Six|1 run|Four|no run|[2-5] wides|wide|no ball),( penalty 5 runs,)?)|(?:out (?:caught by [a-zA-Z-() ]+!!?|Bowled!!?|Stumped!!?|Caught&Bowled!!?|[a-zA-Z- ]+ Run Out!!?(?: [1-6] runs? completed\.)?|Lbw!!?))).+'    
    pattern2=r'(.+) \d+\(\d+\)(?: \[4s-\d+ 6s-\d+\])?'
    
    for ball_data in commentary:
        if matches:=re.search(pattern,ball_data,re.IGNORECASE) :
            bowler,Batman,score1,penalty=matches.groups()
            Bat=find_batman_index(Batsmans,Batman)
            Ball=find_bowler_index(Bowlers,bowler)     
                       
            if penalty: 
                Team_Score+=5
                Extras+=5 
                       
            score=[i.strip() for i in score1.split(',') if i]   
            if len(score) == 1 and 'out' not in score[0]:
                if score[0] in scores:
                    Team_Score,maiden=temp(Bat,Ball,scores,score,Team_Score,maiden)
                    over+=1
                    Ball.overs+=0.1
                elif score[0] in others :   
                    runs=others.index(score[0])-2
                    if runs==0 : 
                        runs+=1
                        Bat.balls_faced+=1
                    Ball.runs_given+=runs    
                    Team_Score+=runs
                    Extras+=runs
                    maiden=100
            elif len(score) == 2 :
                try:
                    if others.index(score[0]) == 2 :
                        Team_Score,maiden=temp(Bat,Ball,scores,score,Team_Score,maiden,1,1)  
                        Extras+=1   
                        maiden=100  
                    else :
                        Bat.balls_faced+=1
                        runs=scores.index(score[1]) 
                        Team_Score+=runs   
                        Extras+=runs    
                        over+=1
                        Ball.overs+=0.1
                        maiden+=1      
                except :
                    print(score1)         
            elif 'out' in score[0]:
                over+=1
                Wickets+=1
                maiden+=1
                name=matches.group(2).split()[0]
                Bat.balls_faced+=1
                Ball.overs+=0.1
                if 'Run Out' in score[0]:
                    if other:=re.search(r'.+out (.+) Run Out!(?:!)?(?: ([1-6]) runs? completed.)?.+',ball_data) :
                        if other.group(2):
                            Bat.runs_made+=int(other.group(2))
                            Team_Score+=int(other.group(2))
                            Ball.runs_given+=int(other.group(2))
                        Bat=find_batman_index(Batsmans,other.group(1))
                        
                    name=score[0].split()[1]
                    Ball.wickets-=1
                y=[]
                for i in ball_data.split()[::-1]:
                    y.append(i)
                    if i==name: break
                if out_tag:=re.search(pattern2,' '.join(y[::-1])):
                    Bat.status=out_tag.group(1)[len(Bat.Name)+1:]
                Ball.wickets+=1        
            if over == 6 :
                Overs+=1
                over=0
                Ball.overs=round(Ball.overs) 
                if maiden == 6 :
                    Ball.maidens+=1
                maiden=0     
    return Batsmans,Bowlers,Team_Score,Wickets,Extras,Overs,over                            

if __name__=='__main__':
    main() 

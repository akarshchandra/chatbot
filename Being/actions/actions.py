# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import requests
import json 
import sqlite3
import random
import pandas as pd

class ActionHelloWorld(Action):

    def name(self) -> Text:
        return "action_hello_world"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        weigh = str(tracker.get_slot('user_weight'))
        heigh = str(tracker.get_slot('user_height'))
        dispatcher.utter_message(text=weigh)
        dispatcher.utter_message(text=heigh)
        url = "https://body-mass-index-bmi-calculator.p.rapidapi.com/imperial"
        querystring = {"weight":weigh,"height":heigh}
        headers = {
	        "X-RapidAPI-Host": "body-mass-index-bmi-calculator.p.rapidapi.com",
	        "X-RapidAPI-Key": "fd2018254amsh51f1f7bce86b5b4p180c00jsn05bd8f80a054"
        }
        response = requests.request("GET", url, headers=headers, params=querystring)
        dispatcher.utter_message(text=str(response.status_code))
        if response.status_code!=200:
            dispatcher.utter_message(text='could not fetch BMI')
            return [SlotSet("user_bmi",'25')]
        bmij=response.json()
        calc_bmi=bmij['bmi']
        dispatcher.utter_message(text=str(calc_bmi))
        return [SlotSet("user_bmi",calc_bmi)]


class saveUser(Action):

    def name(self) -> Text:
        return "action_save_user"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        currUser=str(tracker.get_slot('user_name'))
        currAge=str(tracker.get_slot('user_age'))
        currWeight=str(tracker.get_slot('user_weight'))
        currHeight=str(tracker.get_slot('user_height'))
        currBMI=str(tracker.get_slot('user_bmi'))
         # connect to DB
        connection = sqlite3.connect('C:/Users/PREOATOR/rasar/actions/master1.db')
        cursor = connection.cursor()
        # save user data to sqlite table
        query= f"""INSERT INTO user_record (NAME,AGE,HEIGHT,WEIGHT,BMI) VALUES ("{currUser}","{currAge}","{currHeight}","{currWeight}","{currBMI}");"""
        cursor.execute(query) 
        connection.commit()
        dispatcher.utter_message(attachment="https://giphy.com/embed/CaS9NNso512WJ4po0t")
        connection.close()
        currBMI=float(currBMI)
        if currBMI<20:
            dispatcher.utter_message(text="You can ask me about nutrition")
        elif currBMI>25:
            dispatcher.utter_message(text="You can ask me about workouts")
        else:
            dispatcher.utter_message(text="You can ask me about yoga or books")

        return []

class queryNutrition(Action):

    def name(self) -> Text:
        return "action_query_nutrition"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        currFquery=tracker.get_slot('user_fquery')
        url = "https://nutrition-by-api-ninjas.p.rapidapi.com/v1/nutrition"
        querystring = {"query":currFquery}
        headers = {"X-RapidAPI-Host": "nutrition-by-api-ninjas.p.rapidapi.com","X-RapidAPI-Key": "fd2018254amsh51f1f7bce86b5b4p180c00jsn05bd8f80a054"}
        response = requests.request("GET", url, headers=headers, params=querystring)
        print(response.text)
        if response.status_code!=200:
            dispatcher.utter_message(text='could not fetch nutrition data please try again later')
            return []
        responseList=response.json()
        responseDict=responseList[0]
        keys_values = responseDict.items()
        newDict = {str(key): str(value) for key, value in keys_values}
        responseText=newDict['serving_size_g']+' grams'+' of '+newDict['name']+' has about '+newDict['calories']+' calories '+'with '+newDict['protein_g']+' grams of protein '+newDict['fat_saturated_g']+' grams of fat '+newDict['carbohydrates_total_g']+' grams of carbs and '+newDict['fiber_g']+' grams of fiber'
        dispatcher.utter_message(text=responseText)
        return []

class fetchLabel(Action):

    def name(self) -> Text:
        return "action_query_label"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        Dict = {'snickers':61911 ,'pepsi':2018165,'cheerios':427112,'lays':119388,'toft milk':523531,'cracker jack':202976,'coke zero':1900703}
        currLabquery=tracker.get_slot('user_labquery')
        link=f"https://api.spoonacular.com/food/products/{Dict[currLabquery]}/nutritionLabel.png?apiKey=1777ed1af9924bde9135b4a91b933e87"
        dispatcher.utter_message(image=link)
        return []


class fetchExercise(Action):

    def name(self) -> Text:
        return "action_query_exercise"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        currExquery=str(tracker.get_slot('user_exercisequery'))
        texturl=f"https://api.api-ninjas.com/v1/exercises?muscle={currExquery}"
        headers = {"X-Api-Key": "w6jsXOOzkAiYUKseKY8Cfg==5W8DN1pTY9Yc6dyj"}
        response = requests.request("GET", texturl, headers=headers)
        if response.status_code!=200:
            dispatcher.utter_message(text='could not fetch workout please try again later')
            return []
        rj=response.json()
        exercise=rj[0]
        name=exercise['name']
        instr=exercise['instructions']
        text2=f'you can try {name}, the instructions are as follows:- {instr}'
        dispatcher.utter_message(text=text2)
        namelist=name.split()
        searchstr=''
        if len(namelist) == 1:
            searchstr=namelist[0]
        else:
            for st in namelist:
                searchstr=searchstr+st+'+'
            searchstr=searchstr[:-1]
        
        exerUrl = "https://simple-youtube-search.p.rapidapi.com/search"
        querystring = {"query":searchstr,"safesearch":"false"}
        headers = {"X-RapidAPI-Host": "simple-youtube-search.p.rapidapi.com","X-RapidAPI-Key": "fd2018254amsh51f1f7bce86b5b4p180c00jsn05bd8f80a054"}
        response = requests.request("GET", exerUrl, headers=headers, params=querystring)
        if response.status_code!=200:
            dispatcher.utter_message(text='could not fetch youtube link please try again later')
            return []
        yTExerUrl=str(response.json()['results'][0]['url'])
        dispatcher.utter_message(attachment=yTExerUrl)
        return []
        
class fetchEmotion(Action):

    def name(self) -> Text:
        return "action_query_emotion"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        currEmoquery=tracker.get_slot('user_emotion')
        urlList=['https://www.youtube.com/watch?v=LnJwH_PZXnM','https://www.youtube.com/watch?v=D_Vg4uyYwEk','https://www.youtube.com/watch?v=k9zTr2MAFRg','https://www.youtube.com/watch?v=PfM-iugc2a4','https://www.youtube.com/watch?v=eX2qFMC8cFo']
        Emoturl = "https://text-sentiment.p.rapidapi.com/analyze"
        emolist=currEmoquery.split()
        fs=''
        for s in emolist:
            fs=fs+s+'%20'
        fs=fs[:-3]
        payload = f"text={fs}"
        headers =   {
                        "content-type": "application/x-www-form-urlencoded",
                        "X-RapidAPI-Host": "text-sentiment.p.rapidapi.com",
                        "X-RapidAPI-Key": "fd2018254amsh51f1f7bce86b5b4p180c00jsn05bd8f80a054"
                    }
        response = requests.request("POST", Emoturl, data=payload, headers=headers)
        rj=response.json()
        if rj["pos_percent"]<=rj["neg_percent"]:
            dispatcher.utter_message(text='Sorry to hear that')
            dispatcher.utter_message(text='I think this might help')
            dispatcher.utter_message(attachment=random.choice(urlList))
        else:
             dispatcher.utter_message(text='Want to learn about Yoga?')

        return []

class fetchBook(Action):

    def name(self) -> Text:
        return "action_query_book"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        df1=pd.read_csv('C:/Users/PREOATOR/rasar/actions/Book25.csv')
        idx=random.randint(0, len(df1)-1)
        author=df1['Book-Author'][idx]
        title=df1['Book-Title'][idx]
        bookurl=df1['Image-URL-L'][idx]
        bookText=f'Check out {title} by {author}'
        dispatcher.utter_message(text=bookText)
        dispatcher.utter_message(image=bookurl)
        return []

class fetchHealthTips(Action):

    def name(self) -> Text:
        return "action_query_heathtips"

    def run(self, dispatcher: CollectingDispatcher,tracker: Tracker,domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        hBMI=tracker.get_slot('user_bmi')
        if hBMI is None:
            dispatcher.utter_message(text='Sorry,I could not find your BMI data found please try after you input BMI data')
            return []
        #print(type(hBMI))
        BMIint=float(hBMI)
        if BMIint<20:
            dispatcher.utter_message(text='You seem to be underweight')
            tips1="""1) Eat more frequently.
            2) Choose nutrient-rich foods. 
            3) Exercise.
            4) Watch when you drink. """
                    
            dispatcher.utter_message(text=tips1)
        elif BMIint>25:
            dispatcher.utter_message(text='You seem to be overweight')
            tips2="""1) Eating 5 smaller meals might work better than eating 3 Larger Ones.
            2) Less clories More Food. 
            3) Exercise does more than burn calories.
            4) No Trans-Fat. """
                     
        else:
            dispatcher.utter_message(text='Your weight seems Healthy! keep up the good work')
            tips3="""1) 50 minutes of moderate-intensity aerobic activity per week. 
            2) Staying hydrated. 
            3) Focus on mental health.
            4) Practice wholesome leaving. """
        return []
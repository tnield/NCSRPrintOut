import csv
import pandas as pd
import plotly.graph_objects as go
import plotly
import os
from fpdf import FPDF

def split():
# Splits the parts of the data into part 1 and part 2

# Does not return anything it saves 2 csv files that have the data for parts 1 and 2
# Used to break the data into 2 parts and 2 different csv files 

    part1 = []
    part2 = []
    with open("ExampleData.csv", 'r') as record:
        csvreader_object = csv.reader(record)
        next(csvreader_object)
        for row in csvreader_object:
            if row[0] != "Part 2":
                part1.append(row)
            else:
                for row in csvreader_object:
                    part2.append(row)
    with open('part1.csv', mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(part1)
    with open('part2.csv', mode="w", newline='') as file:
        writer = csv.writer(file)
        writer.writerows(part2)

def dataCleaning(file):
# file = is part1.csv or part2.csv that is made when spilt() is ran
# If part1.csv = Cleans the data and makes 3 columns, Section, Question, Maturity_Level
# If part2.csv = TODO

# Returns a dataframe of the cleaned data i.e. removed empty rows

    data = []
    with open(file, "r") as record:
        csvreader_object = csv.reader(record)
        next(csvreader_object)
        for row in csvreader_object:
            if len(row[0]) < 1:
                continue
            parts = row[0].split('-', 3)
            qid = '-'.join(parts[:3])
            name = parts[3]
            number = int(row[1].strip())
            dataDict = dict(Section=qid,Question=name,Maturity_Level=number)
            data.append(dataDict)
        pd.options.display.max_colwidth = 1000
        df = pd.DataFrame(data)
    return df

def average(NIST, data, section):
# NIST = NISTdict: dictionary of dictionaries that has the ID's and names of each section and sub section in the NSCR question set
# data = the entire NSCR question set that has been cleaned
# section = the name of the section the function will average

# Returns name of the section and its overall average

    avg_sum = 0
    avg_total = 0
    for key in NIST[section].keys():
        currSection = data[data["Section"].str.startswith(key)]
        val = currSection["Maturity_Level"].values
        for i in val:
            avg_sum = avg_sum + i
            avg_total = avg_total + 1
#     return(section, round(avg_sum/avg_total))
    return(section, avg_sum/avg_total)

def subAverage(NIST, data, section):
# NIST = NISTdict: dictionary of dictionaries that has the ID's and names of each section and sub section in the NSCR question set
# data = the entire NSCR question set that has been cleaned
# section = the name of the section the function will sub average

# Returns 2 dictionaries
#       subAvgs = name of the sub section and its average
#       questNum = name of the sub section and each answer that made up the average

    sub_avg_sum = 0
    sub_avg_total = 0
    subAvgs = {}
    questNum = {}
    for key in NIST[section].keys():
        currSection = data[data["Section"].str.startswith(key)]
        val = currSection["Maturity_Level"].values
        for i in val:
            sub_avg_sum = sub_avg_sum + i
            sub_avg_total = sub_avg_total + 1
        sub = round(sub_avg_sum/sub_avg_total) 
        subAvgs[f'{NIST[section][key]}'] = sub
        questNum[f'{NIST[section][key]}'] = f'{val}'
        sub_avg_total = 0
        sub_avg_sum = 0
    return(subAvgs)

def graph(categories,scores,color,title):
# categories = the different labels for each axie
# scores = the averages of each section
# color = the color of the line and fill of the graph
# title = the title of the graph

# Returns a radar chart

    categories = [*categories, categories[0]]
    scores = [*scores, scores[0]]
    fig = go.Figure(
        data=[
            go.Scatterpolar(
                r=scores, 
                theta=categories, 
                name='Section Averages',
                fill='toself',
                line=dict(color=color)
            )
        ],
        layout=go.Layout(
            title=go.layout.Title(text=title),
            polar = dict(
            radialaxis = dict(
            visible = True,
            range = [0,7])),
            showlegend=False)
    )
    plotly.io.write_image(fig, title, format="PNG", scale=None, width=None, height=None, validate=True, engine='auto')
    my_file = title
    base = os.path.splitext(my_file)[0]
    os.rename(my_file, base + '.png')  

def secGraph(NISTdict,data,color):
# NISTdict = the dict of NIST information
# data = the part of the data needing to be graphed
# color = the color of the graph

# Puts the data into a useable format for the graphing function

    sec = []
    scores = []
    for key in NISTdict.keys():
        sec.append(average(NISTdict,data,key)[0])
        scores.append(average(NISTdict,data,key)[1])
    graph(sec,scores,color,"Section Average")
    
def subGraph(NISTdict,data,section,color,title):
# NISTdict = the dict of NIST information
# data = the part of the data needing to be graphed
# section = the section to have the sub sections graphed 
# color = the color of the graph

# Puts the data into a useable format for the graphing function
    sub = []
    scores = []
    for key in subAverage(NISTdict,data,section).keys():
        sub.append(key)
        scores.append(subAverage(NISTdict,data,section).get(key))
    graph(sub,scores,color,title)
    
def secDoubleBar(NIST,data,avgMO,title,institution):
# NIST = the dict of NIST information
# data = the part of the data needing to be graphed
# avgMO = a list of the averages for the 5 main sections of NIST
# title = the name of graph when saved as a png

# Saves a png of a double bar graph
    
    Sections = list(NIST.keys())
    averages = []
    for section in Sections:
        averages.append(average(NIST,data,section)[1])
    fig = go.Figure(data=[
        go.Bar(name=f"{institution} Averages", x=Sections, y=averages, marker=dict(color='red')),
        go.Bar(name='Missouri Averages',x=Sections, y=avgMO, marker=dict(color='blue'))
    ],
    layout=go.Layout(
            yaxis = dict(
            range = [0,7]),
            showlegend=True)
    )
    fig.update_layout(barmode='group')
    plotly.io.write_image(fig, title, format="PNG", scale=None, width=None, height=None, validate=True, engine='auto')
    my_file = title
    base = os.path.splitext(my_file)[0]
    os.rename(my_file, base + '.png')
    
def subDoubleBar(NIST,data,subAvg,title,institution):
# NIST = the dict of NIST information
# data = the part of the data needing to be graphed
# subAvg = a dict of the averages of the sub sections for MO
# title = the name of graph when saved as a png

# Saves a png of a double bar graph
    
    index = 0
    section = ""
    scoresMO = []
    for key in subAvg.keys():
        if index != 0:
            scoresMO.append(subAvg[key])
        else:
            section=section+str(subAvg[key])
            index = index+1
    sub = []
    scores = []
    test = [2,3,4,5,7]
    for key in subAverage(NIST,data,str(section)).keys():
        sub.append(key)
        scores.append(subAverage(NIST,data,str(section)).get(key))
    fig = go.Figure(data=[
        go.Bar(name=f"{institution} Averages", x=sub, y=scores, marker=dict(color='red')),
        go.Bar(name='Missouri Averages',x=sub, y=scoresMO, marker=dict(color='blue'))
    ],
    layout=go.Layout(
            yaxis = dict(    
            range = [0,7]),
            showlegend=True)
    )
    fig.update_layout(barmode='group')
    plotly.io.write_image(fig, title, format="PNG", scale=None, width=None, height=None, validate=True, engine='auto')
    my_file = title
    base = os.path.splitext(my_file)[0]
    os.rename(my_file, base + '.png')
    
def pdf(institution):
# Creates the main handout as a pdf

    section = f"The graph above is the average of the all the sections within the NIST question set. The sections are scored 1 through 7. The numbers represent a maturity level in that particular section. 1 - Not Performed, 2 - Informally Performed, 3 - Documented, 4 - Partially Documented Strandards and/or Procedures, 5- Risk Formally Accepted/Implementation in Process, 6 - Tested and Vertifed, 7- Optimized. Throughout the rest of this readout will be a averages of each of the individual parts of the question set. Below is a graph with averages of the state of Missouri in the same sections compared to {institution}."
    idenfity =f"The activities under this functional area are key for an organizations understanding of their current internal culture, infrastructure, and risk tolerance. This functional area tends to be one of the lowest-rated functions for many organizations. Immature capabilities in the Identify function may hinder an organizations ability to effectively apply risk management principles for cybersecurity. By incorporating sound risk management principles into cybersecurity programs, organizations will be able to continuously align their efforts towards protecting their most valuable assets against the most relevant risks."
    protect=f"The activities under the Protect function pertain to different methods and activities that reduce the likelihood of cybersecurity events from happening and ensure that the appropriate controls are in place to deliver critical services. These controls are focused on preventing cybersecurity events from occurring through common attack vectors, including attacks targeting users and attacks leveraging inherent weakness in applications and network communication."
    detect=f"The quicker an organization can detect a cybersecurity incident, the better positioned it is to be able to remediate the problem and reduce the consequences of the event. Activities found within the Detect function pertain to an organizations ability to identify incidents. These controls are becoming more important, as growing numbers of logs and events within an environment can be overwhelming to handle and make it difficult to identify key concerns."
    respond=f"An organizations ability to quickly and appropriately respond to an incident plays a large role in reducing the incidents consequences. As such, the activities within the Respond function examine how an organization plans, analyzes, communicates, mitigates, and improves its response capabilities. For many organizations, integration and cooperation with other entities is key. Many organizations do not have the internal resources to handle all components of incident response. One example is the ability to conduct forensics after an incident, which helps organizations to identify and remediate the original attack vector. This gap can be addressed through resource-sharing within the SLTT community and leveraging organizations such as MS-ISAC and CISA, which have dedicated resources to provide incident response at no cost to the victim."
    recover=f"Activities within the Recover function pertain to an organizations ability to return to its baseline after an incident has occurred. Such controls are focused not only on activities to recover from the incident, but also on many of the components dedicated to managing response plans throughout their lifecycle."
    pdf = FPDF('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_left_margin(5)
    pdf.set_right_margin(5)
    gx = 5
    gy = 5
    gw = 200
    gh = 0
##### TITLE #####
    pdf.ln(105)
    pdf.set_font('Arial', '', 40)
    pdf.cell(20)
    pdf.multi_cell(0, 20, f"{institution}'s NCSR", 0, 0,'C')
    pdf.cell(25)
    pdf.multi_cell(0, 20, f"Cyber Security Review", 0, 0,'C')
    pdf.set_font('Arial', '', 20)
    pdf.add_page()
##### TABLE OF CONTENT #####
    pdf.ln(20)
    pdf.set_font('Arial', '', 40)
    pdf.cell(50)
    pdf.multi_cell(0, 40, "Table of Contents", 0, 0,'C')
    pdf.set_font('Arial', '', 20)
    pdf.cell(65)
    pdf.multi_cell(0, 20, "5 NIST Sections Overview", 0, 0,'C')
    pdf.cell(58)
    pdf.multi_cell(0, 30, "Identify Sub Sections Averages", 0, 0,'C')
    pdf.cell(58)
    pdf.multi_cell(0, 30, "Protect Sub Sections Averages", 0, 0,'C')
    pdf.cell(58)
    pdf.multi_cell(0, 30, "Detect Sub Sections Averages", 0, 0,'C')
    pdf.cell(58)
    pdf.multi_cell(0, 30, "Respond Sub Sections Averages", 0, 0,'C')
    pdf.cell(58)
    pdf.multi_cell(0, 30, "Recover Sub Sections Averages", 0, 0,'C')
    pdf.cell(78)
    pdf.multi_cell(0, 30, "Part 2 Overview", 0, 0,'C')
##### PAGE 1 #####
    pdf.add_page()
    pdf.image('Section Average.png', gx, gy, gw, gh)
    pdf.line(x1 = 5, y1 = 25, x2 = 205, y2 = 25)
    pdf.ln(5)
    pdf.line(x1 = 5, y1 = 135, x2 = 205, y2 = 135)
    pdf.ln(125)
    pdf.set_font('Arial', '', 9.5)
    pdf.cell(5)
    pdf.multi_cell(0, 10, section, 0, 0,'L')
    pdf.cell(5)
    pdf.image('Section Double Bar.png', 40, 195, 145, 0)
##### PAGE 2 #####  
    pdf.add_page()
    pdf.image('Identify Sub Sections Averages.png', gx, gy, gw, gh)
    pdf.line(x1 = 5, y1 = 25, x2 = 205, y2 = 25)
    pdf.ln(5)
    pdf.line(x1 = 5, y1 = 135, x2 = 205, y2 = 135)
    pdf.ln(125)
    pdf.set_font('Arial', '', 10)
    pdf.cell(5)
    pdf.multi_cell(0, 10, idenfity, 0, 0,'L')
    pdf.cell(5)
    pdf.image('Identify Sub Average Double Bar.png', 40, 195, 145, 0)
##### PAGE 3 #####    
    pdf.add_page()
    pdf.image('Protect Sub Sections Averages.png', gx, gy, gw, gh)
    pdf.line(x1 = 5, y1 = 25, x2 = 205, y2 = 25)
    pdf.ln(5)
    pdf.line(x1 = 5, y1 = 135, x2 = 205, y2 = 135)
    pdf.ln(125)
    pdf.set_font('Arial', '', 10)
    pdf.cell(5)
    pdf.multi_cell(0, 10, protect, 0, 0,'L')
    pdf.cell(5)
    pdf.image('Protect Sub Average Double Bar.png', 40, 195, 145, 0)
##### PAGE 4 #####    
    pdf.add_page()
    pdf.image('Detect Sub Sections Averages.png', gx, gy, gw, gh)
    pdf.line(x1 = 5, y1 = 25, x2 = 205, y2 = 25)
    pdf.ln(5)
    pdf.line(x1 = 5, y1 = 135, x2 = 205, y2 = 135)
    pdf.ln(125)
    pdf.set_font('Arial', '', 9.5)
    pdf.cell(5)
    pdf.multi_cell(0, 10, detect, 0, 0,'L')
    pdf.cell(5)
    pdf.image('Detect Sub Average Double Bar.png', 40, 195, 145, 0)
##### PAGE 5 #####
    pdf.add_page()
    pdf.image('Respond Sub Sections Averages.png', gx, gy, gw, gh)
    pdf.line(x1 = 5, y1 = 25, x2 = 205, y2 = 25)
    pdf.ln(5)
    pdf.line(x1 = 5, y1 = 135, x2 = 205, y2 = 135)
    pdf.ln(125)
    pdf.set_font('Arial', '', 7.3)
    pdf.cell(5)
    pdf.multi_cell(0, 10, respond, 0, 0,'L')
    pdf.cell(5)
    pdf.image('Respond Sub Average Double Bar.png', 40, 195, 145, 0)
##### PAGE 6 #####    
    pdf.add_page()
    pdf.image('Recover Sub Sections Averages.png', gx, gy, gw, gh)
    pdf.line(x1 = 5, y1 = 25, x2 = 205, y2 = 25)
    pdf.ln(5)
    pdf.line(x1 = 5, y1 = 135, x2 = 205, y2 = 135)
    pdf.ln(125)
    pdf.set_font('Arial', '', 9.5)
    pdf.cell(5)
    pdf.multi_cell(0, 10, recover, 0, 0,'L')
    pdf.cell(5)
    pdf.image('Recover Sub Average Double Bar.png', 40, 195, 145, 0)
    
    pdf.output('PrintOut.pdf', 'F')

def clear():
# Removes graph pngs

    os.remove("Section Average.png")
    os.remove("Identify Sub Sections Averages.png")
    os.remove("Protect Sub Sections Averages.png")
    os.remove("Detect Sub Sections Averages.png")
    os.remove("Respond Sub Sections Averages.png")
    os.remove("Recover Sub Sections Averages.png")
    os.remove("Section Double Bar.png")
    os.remove("Identify Sub Average Double Bar.png")
    os.remove("Protect Sub Average Double Bar.png")
    os.remove("Detect Sub Average Double Bar.png")
    os.remove("Respond Sub Average Double Bar.png")
    os.remove("Recover Sub Average Double Bar.png")
    
def main():
  #### NCSR NIST section and sub section ####  

    NISTdict={
    "identify" : {"ID-AM":"Assest Management","ID-BE":"Business Environment","ID-GV":"Goverance","ID-RA":"Risk Assessment","ID-RM":"Risk Management Strategy","ID-SC":"Supply Chain Risk Management"},
    "protect" : {"PR-AC":"Identity Management and Access Control","PR-AT":"Awareness and Training","PR-DS":"Data Security","PR-IP":"Information Protection Process & Procedues","PR-MA":"Maintenance","PR-PT":"Protectice Technology"},
    "detect" : {"DE-AE":"Anomalies and Events","DE-CM":"Security Contunuous Monitoring","DE-DP":"Detection Processes"},
    "respond" : {"RS-RP":"Response Planning","RS-CO":"Communications","RS-AN":"Analysis","RS-MI":"Mitigation","RS-IM":"Improvement"},
    "recover" : {"RC-RP":"Recovery Planning","RC-IM":"Improvements","RC-CO":"Communications" }
    }
    
    #### TEMPLET TO ADD DATA FROM PREVIOUS OR FUTURE YEARS ####
    
#     avg=["","","","",""]
    
#     id={ "Section":"identify", "ID-AM":"","ID-BE":"","ID-GV":"","ID-RA":"","ID-RM":"","ID-SC":""}
#     pr={ "Section":"protect", "PR-AC":"","PR-AT":"","PR-DS":"","PR-IP":"","PR-MA":"","PR-PT":""}
#     de={ "Section":"detect","DE-AE":"","DE-CM":"","DE-DP":""}
#     rs={ "Section":"respond","RS-RP":"","RS-CO":"","RS-AN":"","RS-MI":"","RS-IM":""}
#     rc={ "Section":"recover","RC-RP":"","RC-IM":"","RC-CO":""}

  #### 2022 MISSOURI NCSR ####
    
    avgMO=["3.48","4.10","3.82","3.64","3.55"]
    
    idMO={ "Section":"identify", "ID-AM":"3.74","ID-BE":"3.70","ID-GV":"3.59","ID-RA":"3.69","ID-RM":"3.11","ID-SC":"3.05"}
    prMO={ "Section":"protect", "PR-AC":"4.65","PR-AT":"4.21","PR-DS":"4.03","PR-IP":"3.75","PR-MA":"4.08","PR-PT":"3.85"}
    deMO={ "Section":"detect","DE-AE":"3.71","DE-CM":"4.02","DE-DP":"3.74"}
    rsMO={ "Section":"respond","RS-RP":"3.61","RS-CO":"3.54","RS-AN":"3.66","RS-MI":"3.97","RS-IM":"3.42"}
    rcMO={ "Section":"recover","RC-RP":"3.61","RC-IM":"3.51","RC-CO":"3.53"}

    # Splits the data into 2 parts, part1 and part2
    
    split()
    
    data = dataCleaning('part1.csv')
    
    print('Enter your Institution name:')
    institution = input()
    
    # Creates all the Radar graphs
    secGraph(NISTdict,data,"grey")  
    subGraph(NISTdict,data,"identify","blue","Identify Sub Sections Averages")
    subGraph(NISTdict,data,"protect","brown","Protect Sub Sections Averages")
    subGraph(NISTdict,data,"detect","purple","Detect Sub Sections Averages")
    subGraph(NISTdict,data,"respond","yellow","Respond Sub Sections Averages")
    subGraph(NISTdict,data,"recover","orange","Recover Sub Sections Averages")
    
    # Creates all the Double Bar graphs
    secDoubleBar(NISTdict,data,avgMO,"Section Double Bar",institution)
    subDoubleBar(NISTdict,data,idMO, "Identify Sub Average Double Bar",institution)
    subDoubleBar(NISTdict,data,prMO, "Protect Sub Average Double Bar",institution)
    subDoubleBar(NISTdict,data,deMO, "Detect Sub Average Double Bar",institution)
    subDoubleBar(NISTdict,data,rsMO, "Respond Sub Average Double Bar",institution)
    subDoubleBar(NISTdict,data,rcMO, "Recover Sub Average Double Bar",institution)
    
    pdf(institution)
    
    clear()
    
main()
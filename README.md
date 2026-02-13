This assignment describes the project work expected for COMP30830. Refer also to the lecture notes on Brightspace for more details.

The goal of this project is to develop a web application to display occupancy and weather information for Dublin Bikes.

You will conduct the project in a team using the Scrum methodology.

The project should be submitted Fri 24th April 18:00. This is a hard deadline.

The project will be evaluated based on:
  A) The web application produced (evaluated through a 5 minutes video demo)
  B) The source code of the web application shared in the GitHub repository
  C) The project report
  D) The product backlog (preferably in Google Sheets format)
  E) Individual contribution (evaluated based on declared contribution in the report, and 1-minute presentation per student, incorporated in the video demo, in addition to the 5 minutes)
  
  An adequate multiplier will be assigned based on the contribution of each student to their project, so that:
    Those who did not contribute sufficiently will receive a lower mark or will fail the course, regardless of the quality of the project, AND
    Those who contributed more will be rewarded with an adequate higher mark
    
  NOTE: Every group member is expected to participate to all the items above, and especially to the coding activities.
  
  The computed grade will be adjusted by the lecturer, if considered appropriate, based on a comprehensive evaluation of the items listed above.
  
  Evaluation criteria for each item.
  
  A) Web application
    The web app should include the following main features. The list is not exhaustive, as the students can introduce additional features that they consider relevant.
    1. data collection through JCDecaux API and Openweather App
    2. flask web application (python) running on EC2
    3. display bike stations and occupancy information on a visual map
    4. display weather information
    5. interactivity (click, API request, handle response)
    6. machine learning model for predicting occupancy based on weather patterns, trained on historical data provided.
    One of the following three features:
    7a. Directions/journey planner
    7b. Login 
    7c. Incorporation of generative AI support (e.g., through Gemini API)
    
    The quality of the web application will be evaluated in terms of implemented features and user experience. In particular the application is expected to be a) complete (all features are implemented); b) usable and intuitive.
  
  B) GitHub repository including all the code, documentation, and commit history
    The quality of the code and the GitHub repository will be evaluated in terms of proper structuring, clear comments, clear, modular, and maintainable code. This means that:
    
    The readme of the repository should contain all the information required to navigate the folders and the code, and reuse the project
    
    Principle of separation of concerns, modularity, and cohesion are implemented in the directory structure, and in the internal file structure
    
    Functions have limited length, and they are well commented, with a description of input and output
    
    Folder, file, and variable names clearly communicate their content and meaning
  
  C) Project Report
    A textual report of MAXIMUM 25 pages + Title Page in Times New Roman, 11pt,  including the following sections, with recommended content (more content can be added, if space allows).
  
  Title Page
    Authors; agreed percentage of contribution of each author; type of contribution (code - specifying the features, report, management)
    URL to a 6-8 minutes (MAX) screen recording video in which:
      3-5 minutes: you show and comment the app features with your voice:it needs to clearly show the address of the page so that I can see that it's on EC2.
      3 minutes: each group member presents for 1 minute their contribution.s
    URL of GitHub project
    URL of product and sprint backlogs
    URL to a document in GitHub for Generative AI chats (one for each student)
  
Overview
  Project objectives
  Target users
  Main features (with main screenshot of the final app)
  
Requirements
  Description of the process adopted for requirements elicitation
  Mockup(s) of the app (just most relevant ones)
  List of user stories and associated acceptance criteria
  NOTE: You can add a link to a specific folder of your GitHub repository where you can have additional material associated with the elicitation process, e.g., mockups, personas, interview transcripts, besides those shown in the report.

Architecture and Design
  Diagram of the overall architecture
  Class diagram of the web application and its main elements
  Sequence diagram of the interactions between web application elements
  Description of the aforementioned diagrams
  Database design, with description of design choices
  NOTE: You can add a link to a specific folder of your GitHub repository where you can have additional material associated with architecture and design (e.g., additional diagrams)

Machine Learning Model
  Selected features, feature extraction/data cleaning process, and target variables
  Training and testing process for model selection
  Results and reflection
  NOTE: the code used to train and test the ML model should be shared in the GitHub repository

Testing
  Description of the testing activities performed and results
  
Process
  Description of the organisation and management of the project, including adopted tools
  
For each sprint, include the following information:
  Implemented features/completed work and design decisions in narrative forms
  Burndown chart
  Sprint review
  Sprint retrospective (max 250 words)
  
IMPORTANT: the sprint retrospective (max 250 words) should be submitted by each group at the end of each sprint using the following form: 
https://forms.gle/jeAqgXarzr7R6YBU8

Conclusion
Final remarks, and future works.

The quality of the report will be evaluated in terms of clarity, completeness, and in terms of evidence of a clear and well structured process.

D) Product and spring backlogs
  This will be evaluated based on clarity, organisation, degree of refinement, and quality of work distribution.

Expected work to be carried out in each Sprint:
  Sprint 1: installation of software necessities, definition of user stories/mockups/acceptance criteria, and preliminary implementation of data scraping
  Sprint 2: implementation of data scraping, flask app, and preliminary front-end
  Sprint 3: front-end implementation, refinement, and optional features
  Sprint 4: machine learning model development and tests
  After the four sprints, 2 weeks are left for refactoring, further refinements, and report/code beautification. 

1. Import project from eclipse
- Go to "File >> Open Projects from File System"
- Fill "Import source" with the path of the directory where the project is located
- Press "Finish"

2. Run the program
- Go to "DiCELauncher / src / DiCE / DiceCounterfactuals"
- Run DiceCounterfactuals

Important!: Remember to run the web service (server)

3. How to use the app
- It is only needed to fill the fields marked with a '*' (the run button won't be 
  clickable until this is done)
- Other fields are optional
- The files filter of the model chooser changes in relation to the selected "backend".
  For example if PYT is selected, only .pt files will appear while searching
- The PrivateData radio button is only available when TF2 backend is used
- The input of "Features to vary" and "Continuous Features" must have a JSONArray structure
- The input of "Permitted range", "Features", "Type and precision", "MAD" and
  "Continuous-Features precision" must have a JSONObject structure
- Instance's input is a JSONObject when using DicePrivate and JSONArray
  when using DicePublic (instances array even for just one instance)

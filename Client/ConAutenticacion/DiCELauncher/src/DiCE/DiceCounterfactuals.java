package DiCE;

import java.io.File;
import java.io.IOException;
import java.io.OutputStream;
import java.io.OutputStreamWriter;
import java.io.PrintWriter;
import java.net.URL;
import java.net.URLConnection;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.List;
import javax.swing.JOptionPane;

import org.json.JSONArray;
import org.json.JSONObject;

import Utils.Utilities;
import database.LogIn;


/**
 * Main class of the DiCE package, contains all the logic related with the 
 * obtaining of counterfactuals.
 * It also manages the different views
 * 
 * @author Alejandro Corpas Calvo
 */
public class DiceCounterfactuals {
	private LogIn login;
	private DiceGUI diceGUI;
	private DiceVisualizer visualizer;
	private String token;
	private String URL;
	

	
	public DiceCounterfactuals(String url) {
		this.URL = url;
		this.diceGUI = new DiceGUI(this);
		this.login = new LogIn(this);
		this.visualizer = new DiceVisualizer(diceGUI);
	}
	
	/**
	 * Asks the web service for the required counterfactuals and shows them on a new dialog
	 */
	public void run() {
		JSONObject params = diceGUI.getParams();
		String url = getSelectedURL();
		List<String> counterfactual = new ArrayList<>();
		try {
			counterfactual = getCounterfactual(url, params, diceGUI.getModelFile(), diceGUI.getDataFile());
			visualizer.visualize(counterfactual);
		} catch (IOException e) {
			e.printStackTrace();
			if (e.getMessage().contains("404"))
				System.err.println("Connection error");
			else if (e.getMessage().contains("401")) {
				JOptionPane.showMessageDialog(diceGUI, "Authentication error, try to log in again", "Web error", JOptionPane.ERROR_MESSAGE);
				login.setVisible(true);
			}
			else
				JOptionPane.showMessageDialog(diceGUI, "Unexpected error, check input", "Error", JOptionPane.ERROR_MESSAGE);
		}
	}
	
	/**
	 * The method that sends the request to the web service asking for the counterfactuals
	 * @return A list of strings with the data and counterfactuals  
	 */
	private List<String> getCounterfactual(String url, JSONObject params, File modelFile, File dataFile) throws IOException {
		String charset = "UTF-8";
		String param = params.toString();
		String boundary = Long.toHexString(System.currentTimeMillis());
		String CRLF = "\r\n";		
		
		// The connection with the web service is established
		URLConnection connection = new URL(url).openConnection();
		connection.setDoOutput(true);
		
		// A post request will be sent
        connection.setRequestProperty("Authorization","Bearer " + token);
		connection.setRequestProperty("Content-Type", "multipart/form-data; boundary=" + boundary);
		
		try (OutputStream output = connection.getOutputStream();
		    PrintWriter writer = new PrintWriter(new OutputStreamWriter(output, charset), true);) {
			
		    // For JSON params.
		    writer.append("--" + boundary).append(CRLF);
		    writer.append("Content-Disposition: form-data; name=\"params\"").append(CRLF);
		    writer.append("Content-Type: text/plain; charset=" + charset).append(CRLF);
		    writer.append(CRLF).append(param).append(CRLF).flush();

		    // For model file.
		    writer.append("--" + boundary).append(CRLF);
		    writer.append("Content-Disposition: form-data; name=\"model\"; filename=\"" + modelFile.getName() + "\"").append(CRLF);
		    writer.append("Content-Type: " + URLConnection.guessContentTypeFromName(modelFile.getName())).append(CRLF);
		    writer.append("Content-Transfer-Encoding: binary").append(CRLF);
		    writer.append(CRLF).flush();
		    Files.copy(modelFile.toPath(), output);
		    output.flush();
		    writer.append(CRLF).flush();
		    
		    // For data file when needed.
		    if (dataFile != null) {
		    	writer.append("--" + boundary).append(CRLF);
			    writer.append("Content-Disposition: form-data; name=\"data\"; filename=\"" + dataFile.getName() + "\"").append(CRLF);
			    writer.append("Content-Type: " + URLConnection.guessContentTypeFromName(dataFile.getName())).append(CRLF);
			    writer.append("Content-Transfer-Encoding: binary").append(CRLF);
			    writer.append(CRLF).flush();
			    Files.copy(dataFile.toPath(), output);
			    output.flush();
			    writer.append(CRLF).flush();
		    }
		    
		    // To end the request.
		    writer.append("--" + boundary + "--").append(CRLF).flush();
		}
				
		// The service response is received
		String jsonString = Utilities.getResponse(connection.getInputStream());
		
		// Now the script is executed with the received JSON as parameter
		if (jsonString.startsWith("[")) {
			System.out.println(jsonString.replace("[", "").replace("]", ""));

			//If the string starts with [ means that a PrivateData counterfactual has been received and must be treated differently 
			ArrayList<String> list = new ArrayList<>();
			String[] array = jsonString.replace("[", "").replace("]", "").split(", ");
			for (String s : array)
				list.add(s);
			
			return list;
		}
		else {
			jsonString = jsonString.replace("\"{", "{").replace("}\"", "}").replace("\\\"", "\"").replace("\\\\\"", "\\\"");
			JSONObject jsonObject = new JSONObject(jsonString);
			System.out.println(jsonObject.toString(2));

			List<String> results = new ArrayList<>();
			JSONArray arrayInstances = jsonObject.getJSONArray("test_data");
			for (int i = 0; i < arrayInstances.length(); i++) {
				results.add("Received instance " + i + ":");
				results.add(arrayInstances.getJSONArray(i).getJSONArray(0).toString() + "\n");
				results.add("Counterfactual(s):");
				JSONArray array = (JSONArray) jsonObject.getJSONArray("cfs_list").getJSONArray(i);
				for (Object counterfactual : array)
					results.add(counterfactual.toString());
				results.add("\n");
			}
	        return results;
		}
	}
	
	public void help() {
		try {
			String aux = Utilities.getHelp(getSelectedURL(), token);
			JSONObject obj = new JSONObject(aux);
			JOptionPane.showMessageDialog(diceGUI, obj.toString(2), "Parameters info", JOptionPane.PLAIN_MESSAGE);
		} catch (IOException ex) {
			ex.printStackTrace();
			JOptionPane.showMessageDialog(diceGUI, "Authentication error, try to log in again", "Web error", JOptionPane.ERROR_MESSAGE);
			login.setVisible(true);
		}
	}
	
	/**
	 * @return The URL to call the selected web service method
	 */
	private String getSelectedURL() {
		return (diceGUI.getSelectedMode()) ? URL + "DicePublic" : URL + "DicePrivate";
	}

	/**
	 * @return The URL where the web service is located
	 */
	public String getURL() {
		return URL;
	}
	
	/**
	 * @param Receives the token for the current user
	 */
	public void setToken(String token) {
		this.token = token;
		diceGUI.setVisible(true);
	}
	
	/**
	 * The output field is reset
	 */
	public void resetOutput() {
		visualizer.resetOutput();
		visualizer.setVisible(false);
	}
	
	

	public static void main(String[] args) {
		new DiceCounterfactuals("http://localhost:5444/");
	}
}

package database;

import java.awt.Container;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStream;
import java.io.PrintStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JPanel;
import javax.swing.JTextArea;
import javax.swing.JTextField;

import org.json.JSONObject;

import DiCE.DiceCounterfactuals;
import Utils.Utilities;

public class LogIn extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	private DiceCounterfactuals dice;
	private JTextField username;
	private JTextField password;
	private JLabel infoLabel;
	private String URL;
	
	public LogIn(DiceCounterfactuals dice) {
		this.dice = dice;
		this.URL = dice.getURL();
		this.setTitle("eXplainableAI LogIn");
		initGUI();
	}

	private void initGUI() {
		Container c = this.getContentPane();
		c.setLayout(new BoxLayout(c, BoxLayout.PAGE_AXIS));
		
		String aux = Utilities.getHelp(URL + "register");
		JSONObject objRegister = new JSONObject(aux);
		c.add(new JTextArea(objRegister.toString(2)));
		aux = Utilities.getHelp(URL + "login");
		JSONObject objLogin = new JSONObject(aux);
		c.add(new JTextArea(objLogin.toString(2)));
		
		username = new JTextField();
		c.add(username);
		password = new JTextField();
		c.add(password);
		
		JPanel buttonsPanel = new JPanel();
		buttonsPanel.setLayout(new BoxLayout(buttonsPanel, BoxLayout.LINE_AXIS));
		
		JButton registerButton = new JButton("Register");
		registerButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				register();
				LogIn.this.pack();
			}
		});
		buttonsPanel.add(registerButton);
		JButton loginButton = new JButton("LogIn");
		loginButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				logIn();
				LogIn.this.pack();
			}
		});
		buttonsPanel.add(loginButton);
		c.add(buttonsPanel);
		infoLabel = new JLabel();
		JPanel infoPanel = new JPanel();
		infoPanel.add(infoLabel);
		c.add(infoPanel);
		this.setSize(350, 100);
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);
		this.pack();
		this.setVisible(true);
	}
	
	private void register() {
		infoLabel.setText("Creating JSON file...");
		createLoginJSON(username.getText(), password.getText());
		infoLabel.setText("Created JSON file");
		String charset = "UTF-8";
		File inputFile = new File("login.json");
		
		// The connection with the web service is established
		infoLabel.setText("Connecting to web service...");
		try {
			HttpURLConnection connection = (HttpURLConnection)new URL(URL + "register").openConnection();
			
			// A post request will be sent
			connection.setRequestMethod("POST");
			connection.setRequestProperty("Content-Type", "application/json; charset=" + charset);
			connection.setRequestProperty("Accept", "application/json");
			connection.setDoOutput(true);
			
			try (OutputStream output = connection.getOutputStream()) {
			    Files.copy(inputFile.toPath(), output);
			    output.flush();
			}

			// The service response is received
			String jsonString = Utilities.getResponse(connection.getInputStream());
			JSONObject json = new JSONObject(jsonString);
			if (json.getString("message").contains("was created")) {
				infoLabel.setText("Connected successfully");
				String token = json.getString("access_token");
				dice.setToken(token);
				this.setVisible(false);
				dice.setVisible(true);
				username.setText("");
				password.setText("");
				infoLabel.setText("");
			}
			else {
				infoLabel.setText(json.getString("message"));
				username.setText("");
			}
		} catch (IOException e) {
			infoLabel.setText("Error, connection couldn't be opened");
		}
	}

	private void logIn() {
		infoLabel.setText("Creating JSON file...");
		createLoginJSON(username.getText(), password.getText());
		infoLabel.setText("Created JSON file");
		String charset = "UTF-8";
		File inputFile = new File("login.json");
		
		// The connection with the web service is established
		infoLabel.setText("Connecting to web service...");
		try {
			HttpURLConnection connection = (HttpURLConnection)new URL(URL + "login").openConnection();
			
			// A post request will be sent
			connection.setRequestMethod("POST");
			connection.setRequestProperty("Content-Type", "application/json; charset=" + charset);
			connection.setRequestProperty("Accept", "application/json");
			connection.setDoOutput(true);
			
			try (OutputStream output = connection.getOutputStream()) {
			    Files.copy(inputFile.toPath(), output);
			    output.flush();
			}

			// The service response is received
			String jsonString = Utilities.getResponse(connection.getInputStream());
			JSONObject json = new JSONObject(jsonString);
			if (json.getString("message").contains("Logged in")) {
				infoLabel.setText("Connected successfully");
				String token = json.getString("access_token");
				dice.setToken(token);
				this.setVisible(false);
				dice.setVisible(true);
				username.setText("");
				password.setText("");
				infoLabel.setText("");
			}
			else {
				infoLabel.setText(json.getString("message"));
				username.setText("");
			}
		} catch (IOException e) {
			infoLabel.setText("Error, connection couldn't be opened");
		}
	}
	
	private void createLoginJSON(String username, String password) {
		if (username.equals("") || password.equals(""))
			infoLabel.setText("All fields must be filled");
		else {
			JSONObject obj = new JSONObject();
			obj.put("username", username);
			obj.put("password", password);
			
			try {
				PrintStream p = new PrintStream(new FileOutputStream(new File("login.json")));
				p.println(obj.toString(2));
				p.close();
			} catch (FileNotFoundException e) {
				e.printStackTrace();
			}
		}
	}
	
	
	/*public static void main(String[] args) {
		new LogIn(new DiceCounterfactuals("http://localhost:5444/"));
	}*/
}

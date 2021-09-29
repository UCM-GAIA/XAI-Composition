package DiCE;
import java.awt.BorderLayout;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;
import java.awt.event.ItemEvent;
import java.awt.event.ItemListener;
import java.io.File;
import javax.swing.BoxLayout;
import javax.swing.ButtonGroup;
import javax.swing.JButton;
import javax.swing.JComboBox;
import javax.swing.JFileChooser;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JRadioButton;
import javax.swing.JSpinner;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SpinnerNumberModel;
import javax.swing.event.DocumentEvent;
import javax.swing.event.DocumentListener;
import javax.swing.filechooser.FileNameExtensionFilter;

import org.json.JSONArray;
import org.json.JSONObject;

/**
 * Main view class of the DiCE package, contains all the java swing code and some
 * methods to provide DiceCounterfactuals data about the user input.
 * 
 * @author Alejandro Corpas Calvo
 */
public class DiceGUI extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	public final static String NO_FILE = "File not selected"; 
	
	private JFileChooser chooser;
	private DiceCounterfactuals dice;
	private JLabel inputModelLabel;
	private JComboBox<String> backendCombo;
	private JComboBox<String> methodCombo;
	private JSpinner targetSpinner;
	private JSpinner counterSpinner;
	private JTextField datanameField;
	private JTextField varyField;
	private JTextArea instanceArea;
	private JRadioButton publicBtn;
	private JRadioButton privateBtn;
	private JButton runButton;
	private JLabel inputDataLabel;
	private JTextField outcomeField;
	private JTextField continuousField;
	private JTextField featuresField;
	private JTextField rangeField;
	private JTextField typeField;
	private JTextField precisionField;
	private JTextField madField;

	public DiceGUI(DiceCounterfactuals dice) {
		this.dice = dice;
		this.setTitle("DiCE Counterfactuals");
		initGUI();
	}
	
	private void initGUI() {
		JPanel mainPanel = createMainPanel();
		chooser = new JFileChooser(System.getProperty("user.dir"));
		this.getContentPane().add(mainPanel);
		this.pack();
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);
	}
	
	/**
	 * The application panel is initialized
	 */
	private JPanel createMainPanel() {
		//Initializes every panel
		JPanel mainPanel = new JPanel(new BorderLayout());
		JPanel generalPanel = createGeneralPanel();
		JPanel publicPanel = createPublicPanel();
		JPanel privatePanel = createPrivatePanel();
		JPanel executionPanel = createExecutionPanel();
		
		completeGeneralPanel(generalPanel, publicPanel, privatePanel, mainPanel);
		
		//Finally every section is included in the panel
		mainPanel.add(generalPanel, BorderLayout.NORTH);
		mainPanel.add(publicPanel, BorderLayout.CENTER);
		mainPanel.add(executionPanel, BorderLayout.SOUTH);
		return mainPanel;
	}

	/**
	 * The general panel is initialized
	 */
	private JPanel createGeneralPanel() {
		JPanel generalPanel = new JPanel();
		generalPanel.setLayout(new BoxLayout(generalPanel, BoxLayout.PAGE_AXIS));
		
		JPanel genPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 0, 10));
		genPanel.add(new JLabel("General parameters"));
		generalPanel.add(genPanel);

		
		JPanel modelPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		modelPanel.add(new JLabel("Model file path*:"));
		JPanel fileModelPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		inputModelLabel = new JLabel("File not selected");
		JButton loadModelButton = new JButton("LOAD");
		loadModelButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				if (backendCombo.getSelectedItem() == "sklearn")
					fileChooserDialog("pkl", inputModelLabel);
				else if (backendCombo.getSelectedItem() == "PYT")
					fileChooserDialog("pt", inputModelLabel);
				else
					fileChooserDialog("h5", inputModelLabel);
			}
		});
		fileModelPanel.add(loadModelButton, BorderLayout.PAGE_START);
		fileModelPanel.add(inputModelLabel, BorderLayout.PAGE_START);
		generalPanel.add(modelPanel);
		generalPanel.add(fileModelPanel);
		
		JPanel backendPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		backendCombo = new JComboBox<>();
		backendCombo.addItem("sklearn");
		backendCombo.addItem("TF1");
		backendCombo.addItem("TF2");
		backendCombo.addItem("PYT");
		backendCombo.setPreferredSize(new Dimension(70, 20));
		backendCombo.addItemListener(new ItemListener() {
			@Override
			public void itemStateChanged(ItemEvent e) {
				configRadioButtons();
			}
		});
		backendPanel.add(new JLabel("Model Backend*:"));
		backendPanel.add(backendCombo);
		generalPanel.add(backendPanel);
		
		JPanel methodPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		methodCombo = new JComboBox<>();
		methodCombo.addItem("random");
		methodCombo.addItem("genetic");
		methodCombo.addItem("kdtree");
		methodCombo.setPreferredSize(new Dimension(70, 20));
		methodCombo.addItemListener(new ItemListener() {
			@Override
			public void itemStateChanged(ItemEvent e) {
				configRadioButtons();
			}
		});
		methodPanel.add(new JLabel("Generation Method*:"));
		methodPanel.add(methodCombo);
		generalPanel.add(methodPanel);
		
		
		JPanel desiredPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		targetSpinner = new JSpinner(new SpinnerNumberModel(0, 0, null, 1));
		targetSpinner.setPreferredSize(new Dimension(40, 20));
		desiredPanel.add(new JLabel("Target Class*:"));
		desiredPanel.add(targetSpinner);
		generalPanel.add(desiredPanel);
		
		
		JPanel counterPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		counterSpinner = new JSpinner(new SpinnerNumberModel(1, 1, null, 1));
		counterSpinner.setPreferredSize(new Dimension(40, 20));
		counterPanel.add(new JLabel("Number of CFs*:"));
		counterPanel.add(counterSpinner);
		generalPanel.add(counterPanel);
		
		
		JPanel varyPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		varyPanel.add(new JLabel("Features to vary:"));
		generalPanel.add(varyPanel);
		
		varyField = new JTextField();
		varyField.setPreferredSize(new Dimension(100, 20));
		generalPanel.add(varyField);
		
		
		JPanel datanamePanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		datanamePanel.add(new JLabel("Dataname:"));
		generalPanel.add(datanamePanel);
		
		datanameField = new JTextField();
		datanameField.setPreferredSize(new Dimension(100, 20));
		generalPanel.add(datanameField);
		
		
		JPanel inputPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		inputPanel.add(new JLabel("Instance*:"));
		generalPanel.add(inputPanel);
		
		instanceArea = new JTextArea();
		instanceArea.getDocument().addDocumentListener(new DocumentListener() {
			@Override
			public void removeUpdate(DocumentEvent arg0) {
				configRun(checkFields());
				instanceArea.setSize(new Dimension((int)DiceGUI.this.getSize().getWidth(), instanceArea.getLineCount() * 20));
				DiceGUI.this.pack();

			}
			
			@Override
			public void insertUpdate(DocumentEvent arg0) {
				configRun(checkFields());
				instanceArea.setSize(new Dimension(100, instanceArea.getLineCount() * 20));
				DiceGUI.this.pack();
			}
			
			@Override
			public void changedUpdate(DocumentEvent arg0) {}
		});
		generalPanel.add(instanceArea);
		
		return generalPanel;
	}

	/**
	 * The public panel is initialized
	 */
	private JPanel createPublicPanel() {
		JPanel publicPanel = new JPanel();
		publicPanel.setLayout(new BoxLayout(publicPanel, BoxLayout.PAGE_AXIS));
		
		JPanel dataPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		dataPanel.add(new JLabel("Data file path*:"));
		
		JPanel fileDataPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		inputDataLabel = new JLabel("File not selected");
		JButton loadDataButton = new JButton("LOAD");
		loadDataButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				fileChooserDialog("pkl", inputDataLabel);
			}
		});
		fileDataPanel.add(loadDataButton, BorderLayout.PAGE_START);
		fileDataPanel.add(inputDataLabel, BorderLayout.PAGE_START);
		
		publicPanel.add(dataPanel);
		publicPanel.add(fileDataPanel);
		
		
		JPanel continuousPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		continuousPanel.add(new JLabel("Continuous Features:"));
		publicPanel.add(continuousPanel);
		continuousField = new JTextField();
		continuousField.setPreferredSize(new Dimension(100, 20));
		publicPanel.add(continuousField);
		
		
		JPanel rangePanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		rangePanel.add(new JLabel("Permitted range:"));
		publicPanel.add(rangePanel);
		rangeField = new JTextField();
		rangeField.setPreferredSize(new Dimension(100, 20));
		publicPanel.add(rangeField);
		
		
		JPanel precisionPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		precisionPanel.add(new JLabel("Continuous-Features precision:"));
		publicPanel.add(precisionPanel);
		precisionField = new JTextField();
		precisionField.setPreferredSize(new Dimension(100, 20));
		publicPanel.add(precisionField);
		return publicPanel;
	}

	/**
	 * The private panel is initialized
	 */
	private JPanel createPrivatePanel() {
		JPanel privatePanel = new JPanel();
		privatePanel.setLayout(new BoxLayout(privatePanel, BoxLayout.PAGE_AXIS));

		JPanel outcomePanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		outcomePanel.add(new JLabel("Outcome name*:"));
		privatePanel.add(outcomePanel);
		outcomeField = new JTextField();
		outcomeField.setPreferredSize(new Dimension(100, 20));
		outcomeField.getDocument().addDocumentListener(new DocumentListener() {
			@Override
			public void removeUpdate(DocumentEvent arg0) {
				configRun(checkFields());
			}
			
			@Override
			public void insertUpdate(DocumentEvent arg0) {
				configRun(checkFields());
			}
			
			@Override
			public void changedUpdate(DocumentEvent arg0) {}
		});
		privatePanel.add(outcomeField);
		
		JPanel featuresPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		featuresPanel.add(new JLabel("Features*:"));
		privatePanel.add(featuresPanel);
		featuresField = new JTextField();
		featuresField.setPreferredSize(new Dimension(100, 20));
		featuresField.getDocument().addDocumentListener(new DocumentListener() {
			@Override
			public void removeUpdate(DocumentEvent arg0) {
				configRun(checkFields());
			}
			
			@Override
			public void insertUpdate(DocumentEvent arg0) {
				configRun(checkFields());
			}
			
			@Override
			public void changedUpdate(DocumentEvent arg0) {}
		});
		privatePanel.add(featuresField);
		
		
		JPanel typePanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		typePanel.add(new JLabel("Type and precision:"));
		privatePanel.add(typePanel);
		typeField = new JTextField();
		typeField.setPreferredSize(new Dimension(100, 20));
		privatePanel.add(typeField);
		

		JPanel madPanel = new JPanel(new FlowLayout(FlowLayout.LEFT, 5, 5));
		madPanel.add(new JLabel("MAD:"));
		privatePanel.add(madPanel);
		madField = new JTextField();
		madField.setPreferredSize(new Dimension(100, 20));
		privatePanel.add(madField);
		return privatePanel;
	}

	/**
	 * In this part the execution panel is initialized
	 */
	private JPanel createExecutionPanel() {
		JPanel executionPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 5, 5));

		runButton = new JButton("RUN");
		configRun(false);
		runButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				try {
					dice.run();
					DiceGUI.this.pack();
				} catch (Exception e) {
					e.printStackTrace();
				}
			}
		});
		JButton resetInButton = new JButton("RESET INPUT");
		resetInButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				resetInput();
				DiceGUI.this.pack();
			}
		});
		JButton resetOutButton = new JButton("RESET OUTPUT");
		resetOutButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				resetOutput();
				DiceGUI.this.pack();
			}
		});
		executionPanel.add(runButton);
		executionPanel.add(resetInButton);
		executionPanel.add(resetOutButton);
		return executionPanel;
	}

	/**
	 * Adds the elements that handle interactions between panels
	 */
	private void completeGeneralPanel(JPanel generalPanel, JPanel publicPanel, JPanel privatePanel, JPanel mainPanel) {
		publicBtn = new JRadioButton("PublicData", true);
		publicBtn.addItemListener(new ItemListener() {
			@Override
			public void itemStateChanged(ItemEvent e) {
				if (e.getStateChange() == ItemEvent.SELECTED) {
					mainPanel.remove(privatePanel);
					mainPanel.add(publicPanel, BorderLayout.CENTER);
					configRun(checkFields());
					DiceGUI.this.pack();
			    }
			    else if (e.getStateChange() == ItemEvent.DESELECTED) {
			    	mainPanel.remove(publicPanel);
					mainPanel.add(privatePanel, BorderLayout.CENTER);
					configRun(checkFields());
					DiceGUI.this.pack();
			    }
			}
		});
		privateBtn = new JRadioButton("PrivateData", false);
		privateBtn.setEnabled(false);
		
		ButtonGroup g = new ButtonGroup();
		g.add(publicBtn);
		g.add(privateBtn);	
		
		JPanel radioPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 5, 5));
		radioPanel.add(publicBtn);
		radioPanel.add(privateBtn);
		generalPanel.add(radioPanel);
		
		JButton helpBtn = new JButton("Help");
		helpBtn.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent e) {
				dice.help();
			}
		});
		JPanel helpPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 5, 5));
		helpPanel.add(helpBtn);
		generalPanel.add(helpPanel);

		JPanel specificPanel = new JPanel(new FlowLayout(FlowLayout.CENTER, 0, 10));
		specificPanel.add(new JLabel("Specific parameters"));
		generalPanel.add(specificPanel);
	}

	private void fileChooserDialog(String fileType, JLabel label) {
		chooser.resetChoosableFileFilters();
		chooser.setFileFilter(new FileNameExtensionFilter(String.format("Archivo %s (*.%s)", fileType.toUpperCase(), fileType), fileType));
		int selection = chooser.showOpenDialog(this);
		if(selection == JFileChooser.APPROVE_OPTION) {
			File file = chooser.getSelectedFile();
			label.setText(file.getAbsolutePath());
			configRun(checkFields());
			DiceGUI.this.pack();
		}
		else if (selection == JFileChooser.ERROR_OPTION)
			JOptionPane.showMessageDialog(this,"Input file couldn't be opened due to an error", "File error", JOptionPane.ERROR_MESSAGE);
	}

	/**
	 * @return A JSONObject that contains the configuration parameters for the web service method
	 */
	public JSONObject getParams() {
		// The JSONObject is created and filled
		JSONObject obj = new JSONObject();
		
		// Values in general panel
		obj.put("features_to_vary", (!varyField.getText().equals("") && !varyField.getText().equals("all")) ? new JSONArray(varyField.getText()) : "all");
		obj.put("backend", backendCombo.getSelectedItem());
		obj.put("method", methodCombo.getSelectedItem());
		obj.put("desired_class", targetSpinner.getValue());
		obj.put("num_cfs", counterSpinner.getValue());
		if (!datanameField.getText().equals("")) obj.put("data_name", datanameField.getText());
		
		if (instanceArea.getText().startsWith("{"))
			obj.put("instance", new JSONObject(instanceArea.getText()));
		else
			obj.put("instances", new JSONArray(instanceArea.getText()));
		
		if (!privateBtn.isSelected()) {
			// Values in public panel
			obj.put("cont_features", (!continuousField.getText().equals("")) ? new JSONArray(continuousField.getText()) : new JSONArray());
			if (!rangeField.getText().equals("")) obj.put("permitted_range", new JSONObject(rangeField.getText()));
			if (!precisionField.getText().equals("")) obj.put("continuous_features_precision", new JSONObject(precisionField.getText()));
		}
		
		else {
			// Values in private panel
			obj.put("outcome_name", outcomeField.getText());
			obj.put("features", new JSONObject(featuresField.getText()));
			if (!typeField.getText().equals("")) obj.put("type_and_precision", new JSONObject(typeField.getText()));
			if (!madField.getText().equals("")) obj.put("mad", new JSONObject(madField.getText()));
		}
		
		return obj;
	}
	
	/**
	 * @return Model's file
	 */
	public File getModelFile() {
		return new File(inputModelLabel.getText());
	}

	/**
	 * @return Data's file or null if PrivateData is used
	 */
	public File getDataFile() {
		return (!inputDataLabel.getText().equals(NO_FILE)) ? new File(inputDataLabel.getText()) : null;
	}
	
	/**
	 * @return A boolean that tells the selected mode to run (true = public, false = private)
	 */
	public boolean getSelectedMode() {
		return !privateBtn.isSelected();
	}
	
	/**
	 * Returns every data field to its original state
	 */
	private void resetInput() {
		inputModelLabel.setText(NO_FILE);
		backendCombo.setSelectedIndex(0);
		methodCombo.setSelectedIndex(0);
		targetSpinner.setValue(((SpinnerNumberModel) targetSpinner.getModel()).getMinimum());
		counterSpinner.setValue(((SpinnerNumberModel) counterSpinner.getModel()).getMinimum());
		datanameField.setText("");
		instanceArea.setText("");
		inputDataLabel.setText(NO_FILE);
		continuousField.setText("");
		featuresField.setText("");
		rangeField.setText("");
		typeField.setText("");
		precisionField.setText("");
		madField.setText("");
	}
	
	/**
	 * The output field is reset
	 */
	private void resetOutput() {
		dice.resetOutput();
	}
	
	
	//Miscellaneous methods
	private void configRadioButtons() {
		if (backendCombo.getSelectedItem() == "TF2" && methodCombo.getSelectedItem() != "kdtree")
			privateBtn.setEnabled(true);
		else {
			privateBtn.setEnabled(false);
			publicBtn.setSelected(true);
		}
	}
	
	private void configRun(boolean enable) {
		if (enable) {
			runButton.setEnabled(true);
			runButton.setToolTipText(null);
		}
		else {
			runButton.setEnabled(false);
			runButton.setToolTipText("More data needed");
		}
	}
	
	private boolean checkFields(){
		if (inputModelLabel.getText().equals(NO_FILE) || instanceArea.getText().isEmpty())
			return false;
		else {
			if (publicBtn.isSelected()) {
				if (inputDataLabel.getText().equals(NO_FILE)) 
					return false;
				else
					return true;
			}
			else {
				if (outcomeField.getText().equals("") || featuresField.getText().equals("")) 
					return false;
				else 
					return true;
			}
		}
	}
}

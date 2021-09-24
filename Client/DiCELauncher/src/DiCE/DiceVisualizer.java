package DiCE;

import java.awt.Dimension;
import java.util.List;

import javax.swing.JFrame;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

public class DiceVisualizer extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private JTextArea output;

	public DiceVisualizer() {
		this.setTitle("DiCE Output");
		initGUI();
	}
	
	private void initGUI() {
		JPanel mainPanel = new JPanel();
		output = new JTextArea();
		output.setEditable(false);
		output.setLineWrap(true);
		output.setWrapStyleWord(true);
		output.setSize(new Dimension(400, 800));
		mainPanel.add(new JScrollPane(output));
		this.getContentPane().add(mainPanel);
		this.pack();
		this.setDefaultCloseOperation(DISPOSE_ON_CLOSE);
	}


	public void visualize(List<String> counterfactual) {
		if (counterfactual.isEmpty())
        	output.setText(output.getText() + "An error ocurred. Revise the input parameters\n\n");
        else {
        	for (String s : counterfactual)
            	output.setText(output.getText() + s + '\n');
        	output.setText(output.getText() + "\n\n");
        }
		this.setVisible(true);
	}

	public void resetOutput() {
		output.setText("");
	}

}

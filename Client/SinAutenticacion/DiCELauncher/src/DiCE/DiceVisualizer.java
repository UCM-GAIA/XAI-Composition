package DiCE;

import java.awt.Dimension;
import java.util.List;

import javax.swing.JDialog;
import javax.swing.JFrame;
import javax.swing.JScrollPane;
import javax.swing.JTextArea;

public class DiceVisualizer extends JDialog {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	private JTextArea output;

	public DiceVisualizer(JFrame parent) {
		this.setTitle("DiCE Output");
		this.setLocationRelativeTo(parent);
		initGUI();
	}
	
	private void initGUI() {
		output = new JTextArea();
		output.setEditable(false);
		output.setLineWrap(true);
		output.setWrapStyleWord(true);
		JScrollPane scroll = new JScrollPane (output, JScrollPane.VERTICAL_SCROLLBAR_AS_NEEDED, JScrollPane.HORIZONTAL_SCROLLBAR_AS_NEEDED);
		this.add(scroll);
		this.setSize(new Dimension(400, 400));
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

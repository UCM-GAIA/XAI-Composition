package View;

import java.awt.BorderLayout;
import java.awt.Container;
import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

import javax.swing.BoxLayout;
import javax.swing.JButton;
import javax.swing.JFrame;

import DiCE.DiceCounterfactuals;

public class XAIGUI extends JFrame {
	/**
	 * 
	 */
	private static final long serialVersionUID = 1L;
	
	public XAIGUI() {
		this.setTitle("eXplainableAI Launcher");
		initGUI();
	}
	
	private void initGUI() {
		JButton diceButton = new JButton("DiCE");
		diceButton.addActionListener(new ActionListener() {
			@Override
			public void actionPerformed(ActionEvent arg0) {
				new DiceCounterfactuals("http://localhost:5444/");
				XAIGUI.this.setVisible(false);
			}
		});
		Container c = this.getContentPane();
		c.setLayout(new BoxLayout(c, BoxLayout.PAGE_AXIS));
		c.add(diceButton, BorderLayout.CENTER);
		this.setSize(350, 100);
		this.setDefaultCloseOperation(EXIT_ON_CLOSE);
		this.setVisible(true);
	}
	
	
	
	public static void main(String[] args) {
		new XAIGUI();
		System.out.println("Better run DiceCounterfactuals' main");
	}
}

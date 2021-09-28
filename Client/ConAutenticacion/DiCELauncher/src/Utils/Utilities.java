package Utils;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

public final class Utilities {
	public static final String SERVER_ERROR = "Error getting data. The connection may be closed.";

	public static String getResponse(InputStream inputStream) throws IOException {
		BufferedReader streamReader = new BufferedReader(new InputStreamReader(inputStream, "UTF-8"));
		StringBuilder responseStrBuilder = new StringBuilder();

		String inputStr;
		while ((inputStr = streamReader.readLine()) != null)
			responseStrBuilder.append(inputStr);
		inputStream.close();
		return responseStrBuilder.toString();
	}
	
	public static String getHelp(String URL) {
		try {
			HttpURLConnection connection = (HttpURLConnection) new URL(URL).openConnection();
			connection.setRequestMethod("GET");
			return getResponse(connection.getInputStream());
		} catch (IOException e) {
			e.printStackTrace();
			return SERVER_ERROR;
		}
	}
	
	public static String getHelp(String URL, String token) throws IOException {
		HttpURLConnection connection = (HttpURLConnection) new URL(URL).openConnection();
		connection.setRequestProperty("Authorization","Bearer " + token);
		connection.setRequestMethod("GET");
		return getResponse(connection.getInputStream());
	}

}

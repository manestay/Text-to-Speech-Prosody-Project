package coref;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.util.*;

import edu.stanford.nlp.ling.CoreAnnotations.*;
import edu.stanford.nlp.ling.CoreLabel;
import edu.stanford.nlp.pipeline.Annotation;
import edu.stanford.nlp.pipeline.StanfordCoreNLP;
import edu.stanford.nlp.util.CoreMap;

/**
 * Handles getting parts of speech from Stanford CoreNLP and exports into a
 * text file with the words and their parts of speech
 * @author Kara Schechtman kws2121
 * @version 01.09.2018
 */
public class StanfordPoS {
	private static int TOTAL_SESSION_NUMS = 12;
	private static String ORDER_TYPE = "INTERPOLATED";
	/**
	 * Main method to read in file and output to stdout the coreference chains
	 * @param args
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		parsePoS();
	}

	/**
	 * Run PoS tagging on files 01-12.txt and save results in format ##words.txt
	 * @throws IOException
	 */
	public static void parsePoS() throws IOException {
		for (int i = 1; i <= TOTAL_SESSION_NUMS;i++) {
			String formatted = String.format("%02d", i);
			stanfordTag(formatted + "_" + ORDER_TYPE + ".txt");
		}
	}

	/**
	 * Helper to read in the text of filename, parse using StanfordNLP parser, and save all the PoS tags to a file
	 * @param filename the filename to read
	 */
	private static void stanfordTag(String filename) throws IOException {
		Annotation document = null;
		try {
			document = new Annotation(readFile(filename));
		} catch (FileNotFoundException e) {
			// catch block
			e.printStackTrace();
		}
		Properties props = new Properties();
		props.setProperty("annotators", "tokenize,ssplit,pos,lemma,ner,parse,mention,coref");
		StanfordCoreNLP pipeline = new StanfordCoreNLP(props);
		pipeline.annotate(document);
		List<CoreMap> sentences = document.get(SentencesAnnotation.class);
		String num = filename.substring(0, filename.lastIndexOf("."));
		String save = num + "words.txt";

		BufferedWriter output = null;
		try {
		    File file = new File(save);
		    output = new BufferedWriter(new FileWriter(file));
		    for(CoreMap sentence: sentences) {
				  for (CoreLabel token: sentence.get(TokensAnnotation.class)) {
				    // text of the word
				    String word = token.get(TextAnnotation.class);
				    // POS tag of the word
				    String pos = token.get(PartOfSpeechAnnotation.class);
				    String postag = word + " " + pos + "\n";
				    System.out.println(postag);
				    output.write(postag);
				  }
			}
			output.close();
		} catch ( IOException e ) {
			e.printStackTrace();
		}
	}

	/**
	 * Helper to read in a file into a string
	 * @param filename the file to read
	 * @return the string of the filetext
	 * @throws FileNotFoundException
	 */
	private static String readFile(String filename) throws FileNotFoundException {
		Scanner scanner = new Scanner(new File(filename));
		String entireFileText = scanner.useDelimiter("\\A").next();
		scanner.close();
		return entireFileText;
	}
}

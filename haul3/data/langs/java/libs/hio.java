// HAUL I/O for Java
package wtf.haul;

import java.util.*;

interface IMain {
	/*public static void main(String[] args);*/
	void _main();
}

class hio {
	
	public static void put(String data) {
		System.out.println(data);
		//System.out.flush();
	}
	public static void put_direct(String data) {
		System.out.print(data);
	}
	public static void shout(String data) {
		System.err.println(data);
	}
	
	public static String fetch() {
		Scanner scan = new Scanner(System.in);
		return scan.next();
	}
	
}
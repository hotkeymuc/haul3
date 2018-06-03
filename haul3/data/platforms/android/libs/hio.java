// HAUL I/O for Android
package wtf.haul;

import java.util.*;

import android.util.*;
//import android.os.Handler;
import android.app.Activity;
import android.content.Context;

import android.widget.EditText;
import android.content.DialogInterface;
import android.app.AlertDialog;
import android.app.AlertDialog.Builder;

interface IMain {
	/*public static void main(String[] args);*/
	public void _main();
}
interface IHIO_putter {
	void put(String data);
	void put_direct(String data);
	void shout(String data);
}

class hio {
	
	//public static Handler _handler;
	//public static Thread _mainThread;
	public static Context _context;
	public static Activity _activity;
	
	public static IHIO_putter _putter;
	
	public static void put(String data) {
		Log.i("haul", data);
		System.out.println(data);
		//System.out.flush();
		
		if (_putter != null) _putter.put(data);
	}
	public static void put_(String data) {
		Log.i("haul", data);
		System.out.print(data);
		
		if (_putter != null) _putter.put_direct(data);
	}
	public static void shout(String data) {
		Log.w("haul", data);
		System.err.println(data);
		
		if (_putter != null) _putter.shout(data);
	}
	
	public static Object _fetchSyncToken = new Object();
	private static String _fetchResult = null;
	
	public static String fetch() {
		//Scanner scan = new Scanner(System.in);
		//return scan.next();
		
		_fetchResult = null;
		
		
		final EditText txtUrl = new EditText(_context);
		txtUrl.setHint("some hint");
		
		
		_activity.runOnUiThread(new Runnable() {
			@Override
			public void run() {
				
				new AlertDialog.Builder(_context)
					.setTitle("HAUL I/O fetch")
					.setMessage("Enter some text")
					.setView(txtUrl)
					.setPositiveButton("OK", new DialogInterface.OnClickListener() {
						public void onClick(DialogInterface dialog, int whichButton) {
							
							synchronized(hio._fetchSyncToken) {
								hio._fetchResult = txtUrl.getText().toString();
								hio._fetchSyncToken.notify();
							}
						}
					})
					.setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
						public void onClick(DialogInterface dialog, int whichButton) {
							
							synchronized(hio._fetchSyncToken) {
								hio._fetchResult = "";
								hio._fetchSyncToken.notify();
							}
							
						}
					})
					.show(); 
				
			}
		});
		
		
		// Wait for result
		
		while (_fetchResult == null) {
			
			synchronized (_fetchSyncToken) {
				try {
					//Thread.sleep(100);
					_fetchSyncToken.wait();
				} catch(Exception e) {
					e.printStackTrace();
				}
			}
		}
		
		
		
		return _fetchResult;
	}
	
}
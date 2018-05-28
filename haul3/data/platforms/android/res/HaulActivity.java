package wtf.haul;

import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;

import android.view.View;
import android.view.Window;
import android.widget.TextView;
import android.graphics.Typeface;
//import android.util.Log;

public class HaulActivity extends Activity implements IHIO_putter {
	
	private Thread mainThread;
	
	private static final String NL = System.getProperty("line.separator");	// \n
	private TextView tv;
	private Handler tvHandler;
	
	@Override
	protected void onCreate(Bundle savedInstanceState) {
		super.onCreate(savedInstanceState);
		//setContentView(R.layout.activity_main);
		
		this.requestWindowFeature(Window.FEATURE_NO_TITLE);
		
		hio._activity = this;
		hio._context = this;
		
		
		// Create a text field to output text
		this.tv = new TextView(this);
		//this.tv.setText("HaulActivity" + NL);
		this.tv.setTypeface(Typeface.MONOSPACE);
		this.tv.setSingleLine(false);
		
		this.setContentView(this.tv);
		
		// Re-direct all calls to hio.put etc. to this class
		hio._putter = this;
		
		
		// Problem: E AndroidRuntime: android.view.ViewRootImpl$CalledFromWrongThreadException: Only the original thread that created a view hierarchy can touch its views.
		// Solution: Create a handler to allow other threads to post text to it
		this.tvHandler = new Handler(new Handler.Callback() {
			@Override
			public boolean handleMessage(Message stringMessage) {
				//textView.append((String) stringMessage.obj);
				tv.setText(tv.getText() + (String)stringMessage.obj);
				return true;
			}
		});
		
		
		
		// Now invoke the main code
		//shellmini.main();
		
		//String[] args = new String[0];
		//HaulInfo.MainClass.main(args);
		
		//HaulInfo.MainClass._main();
		
		Runnable r = new Runnable() {
			@Override
			public void run() {
				HaulInfo.MainClass._main();
			}
		};
		this.mainThread = new Thread(r);
		this.mainThread.start();
		
	}
	
	public void put(String data) {
		this.put_direct(data + NL);
	}
	public void put_direct(String data) {
		
		// Direct access to tv is only possible from within main thread:
		//this.tv.setText(this.tv.getText() + data);
		
		// Invoke handler to communicate between mainThread and uiThread
		Message stringMessage = Message.obtain(this.tvHandler);
		stringMessage.obj = data;
		stringMessage.sendToTarget();
		
	}
	public void shout(String data) {
		this.put("!! " + data + " !!");
	}
	
}

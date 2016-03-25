/**
 * 
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;
import java.util.List;

import org.apache.commons.io.FileUtils;
import org.apache.commons.lang3.StringUtils;
import org.apache.log4j.Logger;

import com.android.ddmlib.IDevice;
import com.utdallas.s3lab.smvhunter.enumerate.UIEnumerator;

/**
 * Copyright (C) 2013  David Sounthiraraj

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
    
 * @author david
 *
 */
public class NetworkMonitor implements Runnable{
	
	static Logger logger = Logger.getLogger(NetworkMonitor.class);
	
	public static String GET_PID = "%s -s %s shell ps | grep %s | awk '{print $2}'";
	public static String TRACE_PID = "%s -s %s shell strace -p %s -q -f -e trace=network";
	
			
	public IDevice device = null;
	public String application = "";
	
	public NetworkMonitor(IDevice device, String application){
		this.device = device;
		this.application = application;
	}

	/* (non-Javadoc)
	 * @see java.lang.Runnable#run()
	 */
	@Override
	public void run() {
		try {
			//get the pid first
			String pidString = UIEnumerator.execSpecial(String.format(GET_PID, MonkeyMe.adbLocation, device.getSerialNumber(), application));
			if(StringUtils.isEmpty(pidString)){
				logger.error(getStringforPrinting("pid string empty for app ", application, "trying again"));
				Thread.sleep(5000);
				//try again
				pidString = UIEnumerator.execSpecial(String.format(GET_PID, MonkeyMe.adbLocation, device.getSerialNumber(), application));
			}
			logger.debug(getStringforPrinting("pid string for ", application, pidString));
			List<String> outList = new ArrayList<String>();
			if(StringUtils.isNotEmpty(pidString)){
				Process pidCmd = null;
				try{
					//read the strace command output
					pidCmd = execCommand(String.format(TRACE_PID, MonkeyMe.adbLocation, device.getSerialNumber(), pidString));
					
					BufferedReader pidReader = new BufferedReader(new InputStreamReader(pidCmd.getInputStream()));
					String out = "";
					while((out = pidReader.readLine()) != null){
						
						//break the loop if the current thread has been cancelled
						if(Thread.currentThread().isInterrupted()){
							break;
						}
						outList.add(getStringforPrinting(System.currentTimeMillis(), application, out));
						
						if(StringUtils.contains(out, "connect")){
							logger.debug(out);
							FileUtils.write(new File(MonkeyMe.straceOutputLocation), getStringforPrinting(System.currentTimeMillis(), application, out)+"\n", true);
						}
					}
				}finally{
					FileUtils.writeLines(new File(MonkeyMe.straceDumpLocation), outList, true);
					if(pidCmd != null){
						pidCmd.destroy();
					}
				}
				
			}
		} catch (Exception e) {
			logger.error("Error while processing monitoring network for "+ application, e);
		}
	}
	
	public static Process execCommand(String command) throws IOException{
		String cmd[] = {
				"/bin/bash",
				"-c",
				command
		};
		Process pr = Runtime.getRuntime().exec(cmd);
		return pr;
	}
	
	public static String getStringforPrinting(Object... args){
		StringBuilder sb = new StringBuilder();
		for(Object arg: args){
			sb.append(arg);
			sb.append(" ");
		}
		return sb.toString();
	}
	
}
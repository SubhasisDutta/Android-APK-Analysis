/**
 * 
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;

import org.apache.commons.io.FileUtils;
import org.apache.log4j.Logger;

import com.android.ddmlib.IDevice;
import com.utdallas.s3lab.smvhunter.enumerate.WindowUpdate;

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
public class UDPMonitor implements Runnable {

	private IDevice device;
	private static String UDP_CAPTURE = "%s -s %s shell tcpdump -s 0 -vvv udp";
	private static Logger logger = Logger.getLogger(UDPMonitor.class);

	/**
	 * @param device
	 */
	public UDPMonitor(IDevice device) {
		this.device = device;
	}

	/* (non-Javadoc)
	 * @see java.lang.Runnable#run()
	 */
	@Override
	public void run() {
		//start monitoring the udp traffic
		//this is used to reverse map the ip to the domain
		Process pr = null;
		try {
			pr = NetworkMonitor.execCommand(String.format(UDP_CAPTURE, WindowUpdate.adbLocation, device.getSerialNumber()));
			BufferedReader br = new BufferedReader(new InputStreamReader(pr.getInputStream()));
			String s = null;
			
			while((s = br.readLine()) != null){
				String forPrinting = NetworkMonitor.getStringforPrinting(device.getSerialNumber(), System.currentTimeMillis(), "udp dump: ", s);
				FileUtils.write(new File(MonkeyMe.udpDumpLocation), forPrinting+"\n", true);
				logger.debug(forPrinting);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}finally{
			if(pr != null){
				pr.destroy();
			}
		}
		
	}

}

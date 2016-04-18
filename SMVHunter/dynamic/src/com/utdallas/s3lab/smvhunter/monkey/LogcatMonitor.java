/**
 *
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.io.BufferedReader;
import java.io.File;
import java.io.IOException;
import java.io.InputStreamReader;
import java.util.ArrayList;

import org.apache.commons.io.FileUtils;

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
public class LogcatMonitor implements Runnable{

	private IDevice device;
	private static String LOGCAT = "%s -s %s logcat";

	public LogcatMonitor(IDevice device){
		this.device = device;
	}

	/* (non-Javadoc)
	 * @see java.lang.Runnable#run()
	 */
	@Override
	public void run() {

		//monitor the logcat for analysis
		Process pr = null;
		try {
			pr = NetworkMonitor.execCommand(String.format(LOGCAT, WindowUpdate.adbLocation, device.getSerialNumber()));
			BufferedReader br = new BufferedReader(new InputStreamReader(pr.getInputStream()));
			String s = null;

			ArrayList<String> tmpList = new ArrayList<String>();
			while((s = br.readLine()) != null){
				String forPrinting = NetworkMonitor.getStringforPrinting(device.getSerialNumber(), System.currentTimeMillis(), s);
				tmpList.add(forPrinting);

				//write every 100 lines
				if(tmpList.size() == 100){
					FileUtils.writeLines(new File(MonkeyMe.logCatLocation), tmpList, true);
					tmpList.clear();
				}
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

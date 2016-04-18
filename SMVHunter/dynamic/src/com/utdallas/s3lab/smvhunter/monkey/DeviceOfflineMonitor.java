/**
 *
 */
package com.utdallas.s3lab.smvhunter.monkey;

import java.util.concurrent.ExecutorService;

import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.math.NumberUtils;
import org.apache.log4j.Logger;

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
 * 
 * @author david
 * This class will monitor the adb for offline devices
 * if found it will force kill and restart
 */
public class DeviceOfflineMonitor implements Runnable{
	static Logger logger = Logger.getLogger(DeviceOfflineMonitor.class);
	private static String LIST_OFFLINE = MonkeyMe.adbLocation+" devices | grep -v List | grep offline | awk '{print $1}' | awk -F- '{print $2}'";
	private static String PID_OF_OFFLINE_DEVICE = "lsof -i :%s | grep LISTEN | awk '{print $2}'";
	private static String EMULATOR_NAME = "ps aux | grep %s | grep emulator-arm | grep -v grep | awk '{print $13}'";
	private static String KILL_EMULATOR = "kill -9 %s";
	public static String START_EMULATOR = "";
	public static boolean stop = false;
	public static ExecutorService exec = null;
	


	/* (non-Javadoc)
	 * @see java.lang.Runnable#run()
	 */
	@Override
	public void run() {

		int count = 0;
		while(true){
			try {
				if(stop){
					//free all the threads
					UIEnumerator.execCommand("killall emulator-arm");
					return;
				}

				try{
					//run every 30 secs
					Thread.sleep(1000*30);
				}catch(InterruptedException ex){
					logger.error("sleep interrupted", ex);
					if(stop){
						//free all the threads
						UIEnumerator.execCommand("killall emulator-arm");
						return;
					}
				}

				////////////////////// adb status check
				//check adb status
				count++;
				if(count%5 == 0){
					String out = UIEnumerator.execSpecial(MonkeyMe.adbLocation+" devices");
					//restart the adb daemon when it does not respond
					//don't know why it happens but after 5-6 hours adb
					//daemon stops responding
					if(!StringUtils.contains(out, "emulator-")){
						UIEnumerator.execSpecial("killall adb");
						UIEnumerator.execSpecial(MonkeyMe.adbLocation+" start-server");
					}
				}
				//kill adb process if the count increases above 100
				String adbCount = UIEnumerator.execSpecial("ps aux | grep adb");
				if(adbCount.split("\\n").length > 100){
					logger.info("number of adb process exceeded 100. Restarting adb");
					UIEnumerator.execSpecial("killall adb");
					UIEnumerator.execCommand(MonkeyMe.adbLocation+" start-server");
				}

				///////////////// adb status check end

				//check for offline devices
				String offlineDevices = UIEnumerator.execSpecial(LIST_OFFLINE);
				//for each device find the pid and process
				for(String device: offlineDevices.split("\\n")){
					if(StringUtils.isEmpty(device)){
						continue;
					}
					logger.error(String.format("%s found offline. processing ", device));
					if(NumberUtils.isNumber(device)){
						//find the pid of the emulator
						String cmd = String.format(PID_OF_OFFLINE_DEVICE, device);
						String offlinePid = UIEnumerator.execSpecial(cmd);

						//now find the emulator name
						final String emulatorName = UIEnumerator.execSpecial(String.format(EMULATOR_NAME, offlinePid));

						//kill the emulator and start another one
						UIEnumerator.execSpecial(String.format(KILL_EMULATOR, offlinePid));
						//wait for a sec
						Thread.sleep(2000);

						logger.info(String.format("killed %s. now starting again", emulatorName));
						//start the emulator in a new thread
						exec.execute(new Runnable() {
							@Override
							public void run() {
								try {
									//start it again
									String out = UIEnumerator.execSpecial(String.format(START_EMULATOR, emulatorName));
									logger.info(String.format("%s started with message ", out));
								} catch (Exception e) {
									logger.error(e);
								}

							}
						});

					}
				}
			}catch (Exception e) {
				logger.error(e);
			}
		}
	}
}

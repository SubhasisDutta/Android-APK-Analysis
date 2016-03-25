/**
 * 
 */
package com.utdallas.s3lab.smvhunter.monkey;

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
 *
 */
public class StaticResultBean{
	private String seedName;
	private String seedType;
	
	/**
	 * @param seedName
	 * @param seedType
	 */
	public StaticResultBean(String seedName, String seedType) {
		super();
		this.seedName = seedName;
		this.seedType = seedType;
	}
	/**
	 * @return the seedName
	 */
	public String getSeedName() {
		return seedName;
	}
	/**
	 * @param seedName the seedName to set
	 */
	public void setSeedName(String seedName) {
		this.seedName = seedName;
	}
	/**
	 * @return the seedType
	 */
	public String getSeedType() {
		return seedType;
	}
	/**
	 * @param seedType the seedType to set
	 */
	public void setSeedType(String seedType) {
		this.seedType = seedType;
	}
}

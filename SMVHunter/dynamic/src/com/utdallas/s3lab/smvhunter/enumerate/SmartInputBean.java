package com.utdallas.s3lab.smvhunter.enumerate;

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
 * @author swarup
 *
 */
public class SmartInputBean {
	
	private String name;
	private String id;
	private String type;
	private String variations;
	private String flag;
	
	
	/**
	 * Constructor
	 * @param name
	 * @param id
	 * @param type
	 * @param variations
	 * @param flag
	 */
	public SmartInputBean(String name, String id, String type, String variations, String flag) {
		super();
		this.name = name;
		this.id = id;
		this.type = type;
		this.variations = variations;
		this.flag = flag;
	}
	
	/**
	 * Get Name
	 * @return name
	 */
	public String getName() {
		return name;
	}
	
	/**
	 * Set Name
	 * @param name
	 */
	public void setName(String name) {
		this.name = name;
	}
	
	/**
	 * Get ID
	 * @return id
	 */
	public String getId() {
		return id;
	}
	
	/**
	 * Set ID
	 * @param id
	 */
	public void setId(String id) {
		this.id = id;
	}
	
	/**
	 * Get Input Type
	 * @return type
	 */
	public String getType() {
		return type;
	}
	
	/**
	 * Set Type
	 * @param type
	 */
	public void setType(String type) {
		this.type = type;
	}
	
	/**
	 * Get input variations
	 * @return
	 */
	public String getVariations() {
		return variations;
	}
	
	/**
	 * Set input variation
	 * @param variations
	 */
	public void setVariations(String variations) {
		this.variations = variations;
	}
	
	/**
	 * get input flag
	 * @return
	 */
	public String getFlag() {
		return flag;
	}
	
	/**
	 * Set input flag
	 * @param flag
	 */
	public void setFlag(String flag) {
		this.flag = flag;
	}

}

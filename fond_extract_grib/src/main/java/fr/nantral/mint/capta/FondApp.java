
package fr.nantral.mint.capta;

import org.apache.commons.cli.*;
import java.util.*;
import ucar.ma2.DataType;
import ucar.ma2.Range;
import ucar.nc2.NetcdfFiles;
import ch.qos.logback.classic.Level;
import ch.qos.logback.classic.Logger;
import org.slf4j.LoggerFactory;

import static java.lang.Math.abs;

public class FondApp {
    public static void main(String[] args) {
        setupLogger();
        try {
            realMain(args);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    // I wanted to log to STDERR, but couldn't figure out how to configure logback with logback.xml.
    // So instead, I just suppress log messages
    public static void setupLogger() {
        var rootLogger = (Logger) LoggerFactory.getLogger(Logger.ROOT_LOGGER_NAME);
        rootLogger.setLevel(Level.ERROR);
    }

    public static void realMain(String[] args) throws Exception {
        // === Handle command line arguments ===
        var options = new Options();
        options.addOption("netcdf", true, "netcdf input file");
        options.addOption("lat", true, "latitude");
        options.addOption("lon", true, "longitude");
      
        var parser = new DefaultParser();
        var cmd = parser.parse(options, args);

        var filename = cmd.getOptionValue("netcdf");
        if (filename == null) {
            throw new Exception("Missing filename");
        }

        // Parse latitude and longitude as floats
        var lat_s = cmd.getOptionValue("lat");
        if (lat_s == null) throw new Exception("Missing latitude");
        var lat = Float.parseFloat(lat_s);
        var lon_s = cmd.getOptionValue("lon");
        if (lon_s == null) throw new Exception("Missing longitude");
        var lon = Float.parseFloat(lon_s);

        System.err.println("filename = " + filename);
        System.err.println("lat, lon = " + lat + ", " + lon);


        // === Do it ===
        try (var nc = NetcdfFiles.open(filename)) {
            // === Print time header and values ===
            var time = nc.findVariable("time");
            var time_desc = time.findAttribute("long_name").getStringValue();
            {
                System.out.println(time_desc);
                var line = new StringBuilder("time: ");
                var my_data = (float[]) time.read().get1DJavaArray(DataType.FLOAT);
                for (var i = 0; i < my_data.length; i++) {
                    if (i != 0) line.append(" ");
                    line.append(my_data[i]);
                }
                System.out.println(line);
            }

            // === Find index for latitude and longitude closest to our point ==
            var lats = (float[]) nc.findVariable("latitude").read().get1DJavaArray(DataType.FLOAT);
            var lons = (float[]) nc.findVariable("longitude").read().get1DJavaArray(DataType.FLOAT);

            var min_lat_i = 0;
            {
                var min_dist = abs(lats[0] - lat);
                for (var i = 0; i < lats.length; i++) {
                    var dist = abs(lats[i] - lat);
                    if (dist < min_dist) {
                        min_dist = dist;
                        min_lat_i = i;
                    }
                }
            }

            var min_lon_i = 0;
            {
                var min_dist = abs(lons[0] - lon);
                for (var i = 0; i < lons.length; i++) {
                    var dist = abs(lons[i] - lon);
                    if (dist < min_dist) {
                        min_dist = dist;
                        min_lon_i = i;
                    }
                }
            }

            System.err.println("i, j = " + min_lat_i + ", " + min_lon_i);

            // === Grab data for each variable we're interested in ===

            // Assume dimensions are *_conc(time=*, level=1, latitude=*, longitude=*)
            var variables = new String[] {"no2_conc", "o3_conc", "pm10_conc", "pm2p5_conc"};
            for (var varname : variables) {
                var my_var = nc.findVariable(varname);
                if (my_var == null) {
                    System.err.println("Missing variable " + varname);
                }

                // Extract the single lat,lon value we chose
                int[] varShape = my_var.getShape();
                List<Range> ranges = new ArrayList();
                ranges.add(null);
                ranges.add(null);
                ranges.add(new Range(min_lat_i, min_lat_i));
                ranges.add(new Range(min_lon_i, min_lon_i));

                // Build and print the string
                var line = new StringBuilder(varname)
                        .append(": ");
                var my_data = (float[]) my_var.read(ranges).get1DJavaArray(DataType.FLOAT);
                for (var i = 0; i < my_data.length; i++) {
                    if (i != 0) line.append(" ");
                    line.append(my_data[i]);
                }

                System.out.println(line);
            }
            
        }
    }
}

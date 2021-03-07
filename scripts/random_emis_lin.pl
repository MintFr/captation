#!/usr/bin/perl

use v5.20;

my $count = shift @ARGV or die "Missing count";

say join "\t", qw<Id NO NO2 PM10 PM25 O3>;
for my $i (0 .. ($count - 1)) {
	say join "\t", ("$i", (rand) x 5);
}

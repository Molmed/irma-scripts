#!/usr/bin/perl -w

use strict;
use JSON;

use lib "/vulpes/ngi/production/latest/sw/arteria/siswrap_venv/deps/sisyphus/sisyphus-latest/lib";
use Molmed::Sisyphus::QStat;

my $data;

foreach my $statdump (@ARGV) {
  my $stat = Molmed::Sisyphus::QStat->new();
  $stat->loadData($statdump);
  
  foreach my $key ("Q30LENGTH", "SEQGC", "SEQUENCES", "SAMPLED_SEQS", "ADAPTER", "QPERBASEANDPOSITIONRESULT") {
    $data->{$statdump}->{$key} = $stat->{$key};
  }


  foreach my $key (keys %{$stat}) {
    unless(ref $stat->{$key}) {
      $data->{$statdump}->{$key} = $stat->{$key};
    }
  }
}

print encode_json($data);

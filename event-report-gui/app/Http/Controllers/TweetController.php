<?php

namespace App\Http\Controllers;

use App\Tweet;
use Illuminate\Support\Facades\DB;
use Illuminate\Http\Request;
use Carbon\Carbon;

class TweetController extends Controller
{
    
    public function rekap() {
        if (request()->route()->named('home')){
            // $start = Carbon::today();
            // $end = Carbon::today()->addDay();

            // $tweets = Tweet::whereBetween('created_at', [$start, $end])->get();

            $tweets = Tweet::all();

            return view('welcome')->with([
                'tweets' => $tweets
            ]);
        }
    }

}
<?php

namespace App;

use Illuminate\Database\Eloquent\Model;

class Tweet extends Model
{
    protected $table = 'tweet';

    protected $fillable = [
        'tweet_id', 'user_id', 'tweet', 'place', 'address', 'latitude', 'longitude'
    ];

}

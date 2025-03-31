chatgpt suggests profiling the code:

```
import cProfile
import mwparserfromhell

sample_text = "''This'' is a test with [[links]], '''bold''', and {{templates}}." * 1000
cProfile.run("mwparserfromhell.parse(sample_text)", sort='cumtime')
```

I get:








         443037 function calls (427037 primitive calls) in 0.235 seconds

   Ordered by: cumulative time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.235    0.235 {built-in method builtins.exec}
        1    0.002    0.002    0.235    0.235 <string>:1(<module>)
   8001/1    0.030    0.000    0.233    0.233 utils.py:37(parse_anything)
        1    0.000    0.000    0.233    0.233 __init__.py:68(parse)
        1    0.007    0.007    0.219    0.219 builder.py:326(build)
16000/8000    0.008    0.000    0.207    0.000 builder.py:318(_handle_token)
     2000    0.024    0.000    0.149    0.000 builder.py:270(_handle_tag)
     2000    0.007    0.000    0.063    0.000 tag.py:33(__init__)
     8001    0.010    0.000    0.032    0.000 builder.py:71(_pop)
    12000    0.009    0.000    0.027    0.000 builder.py:41(<lambda>)
     1000    0.004    0.000    0.023    0.000 builder.py:150(_handle_wikilink)
     1000    0.004    0.000    0.021    0.000 builder.py:109(_handle_template)
    24003    0.013    0.000    0.020    0.000 <frozen importlib._bootstrap>:1390(_handle_fromlist)
     2000    0.001    0.000    0.019    0.000 tag.py:218(tag)
     2000    0.001    0.000    0.017    0.000 tag.py:254(closing_tag)
     2000    0.001    0.000    0.017    0.000 tag.py:222(contents)
    32004    0.011    0.000    0.017    0.000 <frozen importlib._bootstrap>:645(parent)
        1    0.014    0.014    0.014    0.014 {method 'tokenize' of '_tokenizer.CTokenizer' objects}
     8001    0.014    0.000    0.014    0.000 wikicode.py:58(__init__)
    84006    0.013    0.000    0.013    0.000 {built-in method builtins.isinstance}
    12000    0.009    0.000    0.012    0.000 text.py:30(__init__)
     1000    0.001    0.000    0.010    0.000 wikilink.py:31(__init__)
    22000    0.007    0.000    0.010    0.000 tokens.py:50(__getattr__)
     1000    0.001    0.000    0.010    0.000 template.py:40(__init__)
     1000    0.000    0.000    0.009    0.000 template.py:196(name)
     1000    0.000    0.000    0.009    0.000 wikilink.py:70(title)
    16000    0.005    0.000    0.008    0.000 builder.py:79(_write)
     8001    0.006    0.000    0.008    0.000 smart_list.py:54(__new__)
    32004    0.006    0.000    0.006    0.000 {method 'rpartition' of 'str' objects}
    32001    0.005    0.000    0.005    0.000 {method 'pop' of 'list' objects}
    24003    0.004    0.000    0.004    0.000 {built-in method builtins.hasattr}
    24001    0.004    0.000    0.004    0.000 {method 'append' of 'list' objects}
     8001    0.003    0.000    0.004    0.000 builder.py:67(_push)
    12000    0.003    0.000    0.003    0.000 text.py:48(value)
    22000    0.003    0.000    0.003    0.000 {method 'get' of 'dict' objects}
     2000    0.001    0.000    0.002    0.000 tag.py:226(wiki_markup)
     8001    0.001    0.000    0.001    0.000 {built-in method __new__ of type object at 0xa43b40}
     2000    0.001    0.000    0.001    0.000 tag.py:232(self_closing)
     2000    0.000    0.000    0.000    0.000 tag.py:236(invalid)
     2000    0.000    0.000    0.000    0.000 tag.py:240(implicit)
     2000    0.000    0.000    0.000    0.000 tag.py:258(wiki_style_separator)
     2000    0.000    0.000    0.000    0.000 tag.py:244(padding)
     2000    0.000    0.000    0.000    0.000 tag.py:205(closing_wiki_markup)
     1000    0.000    0.000    0.000    0.000 wikilink.py:74(text)
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
        1    0.000    0.000    0.000    0.000 {method 'reverse' of 'list' objects}
        1    0.000    0.000    0.000    0.000 __init__.py:59(__init__)
        1    0.000    0.000    0.000    0.000 builder.py:63(__init__)




# other suggestions

use pypy


# rewriting


Optimization Options
✅ 1. Rewriting the builder.py logic in C or Cython

    Since _handle_token(), _handle_tag(), _pop(), and _push() take a lot of time, moving them to C would improve performance.

    Example approach:

        Convert builder.py into a C extension using Cython or PyO3 (Rust).

        Replace Python list operations with C arrays or Rust vectors.



✅ 3. Optimizing _handle_token() Directly

    _handle_token() processes 16,000 calls, meaning it's a hot spot.

    Instead of rewriting in C immediately, try:

        Reduce Python object allocations (avoid excessive string copies).

        Use caching mechanisms to store common token patterns.

        Optimize _write() calls in builder.py:79, since string concatenation might be slowing things down.






# other output from cprofile.run

(block verbatim)

         443037 function calls (427037 primitive calls) in 0.231 seconds

   Ordered by: standard name

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
    24003    0.013    0.000    0.019    0.000 <frozen importlib._bootstrap>:1390(_handle_fromlist)
    32004    0.011    0.000    0.017    0.000 <frozen importlib._bootstrap>:645(parent)
        1    0.002    0.002    0.231    0.231 <string>:1(<module>)
        1    0.000    0.000    0.000    0.000 __init__.py:59(__init__)
        1    0.000    0.000    0.229    0.229 __init__.py:68(parse)
     1000    0.004    0.000    0.021    0.000 builder.py:109(_handle_template)
     1000    0.003    0.000    0.021    0.000 builder.py:150(_handle_wikilink)
     2000    0.024    0.000    0.143    0.000 builder.py:270(_handle_tag)
16000/8000    0.008    0.000    0.200    0.000 builder.py:318(_handle_token)
        1    0.007    0.007    0.212    0.212 builder.py:326(build)
    12000    0.009    0.000    0.027    0.000 builder.py:41(<lambda>)
        1    0.000    0.000    0.000    0.000 builder.py:63(__init__)
     8001    0.003    0.000    0.004    0.000 builder.py:67(_push)
     8001    0.010    0.000    0.026    0.000 builder.py:71(_pop)
    16000    0.005    0.000    0.008    0.000 builder.py:79(_write)
     8001    0.006    0.000    0.008    0.000 smart_list.py:54(__new__)
     2000    0.000    0.000    0.000    0.000 tag.py:205(closing_wiki_markup)
     2000    0.001    0.000    0.019    0.000 tag.py:218(tag)
     2000    0.001    0.000    0.017    0.000 tag.py:222(contents)
     2000    0.001    0.000    0.002    0.000 tag.py:226(wiki_markup)
     2000    0.001    0.000    0.001    0.000 tag.py:232(self_closing)
     2000    0.000    0.000    0.000    0.000 tag.py:236(invalid)
     2000    0.000    0.000    0.000    0.000 tag.py:240(implicit)
     2000    0.000    0.000    0.000    0.000 tag.py:244(padding)
     2000    0.001    0.000    0.017    0.000 tag.py:254(closing_tag)
     2000    0.000    0.000    0.000    0.000 tag.py:258(wiki_style_separator)
     2000    0.006    0.000    0.063    0.000 tag.py:33(__init__)
     1000    0.000    0.000    0.009    0.000 template.py:196(name)
     1000    0.001    0.000    0.010    0.000 template.py:40(__init__)
    12000    0.009    0.000    0.012    0.000 text.py:30(__init__)
    12000    0.003    0.000    0.003    0.000 text.py:48(value)
    22000    0.007    0.000    0.010    0.000 tokens.py:50(__getattr__)
   8001/1    0.030    0.000    0.229    0.229 utils.py:37(parse_anything)
     8001    0.007    0.000    0.007    0.000 wikicode.py:58(__init__)
     1000    0.001    0.000    0.010    0.000 wikilink.py:31(__init__)
     1000    0.000    0.000    0.009    0.000 wikilink.py:70(title)
     1000    0.000    0.000    0.000    0.000 wikilink.py:74(text)
     8001    0.001    0.000    0.001    0.000 {built-in method __new__ of type object at 0xa43b40}
        1    0.000    0.000    0.231    0.231 {built-in method builtins.exec}
    24003    0.004    0.000    0.004    0.000 {built-in method builtins.hasattr}
    84006    0.013    0.000    0.013    0.000 {built-in method builtins.isinstance}
    24001    0.004    0.000    0.004    0.000 {method 'append' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {method 'disable' of '_lsprof.Profiler' objects}
    22000    0.003    0.000    0.003    0.000 {method 'get' of 'dict' objects}
    32001    0.005    0.000    0.005    0.000 {method 'pop' of 'list' objects}
        1    0.000    0.000    0.000    0.000 {method 'reverse' of 'list' objects}
    32004    0.006    0.000    0.006    0.000 {method 'rpartition' of 'str' objects}
        1    0.017    0.017    0.017    0.017 {method 'tokenize' of '_tokenizer.CTokenizer' objects}


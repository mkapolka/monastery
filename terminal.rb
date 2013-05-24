def prompt
   @continue = true;
   while @continue
      print ">"
      @continue = do_prompt(gets.strip)
   end
end

def do_prompt(string)
   case string
      when "wait"
         wait
      when "look" 
         look
      when "exit" 
         puts "Stopping prompt.";
         return false;
      when "reload!"
         puts "Reloading..."
         reload!
   end

   return true;
end

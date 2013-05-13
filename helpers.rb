#Here are some helper methods that you may find helpful in your writing

class Object
   #Get the metaclass / eigenclass
   def metaclass; class << self; self; end; end
end
